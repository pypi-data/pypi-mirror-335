import argparse
import atexit
import base64
import hashlib
import json
import os
import subprocess
import threading
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Union, Tuple, Dict

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, make_response, request, Request, Response

from streamlit_pyvista import ROOT_URL
from streamlit_pyvista.helpers.cache import (
    save_file_content,
    update_cache,
    DEFAULT_CACHE_DIR,
    DEFAULT_VIEWER_CACHE_NAME,
)
from streamlit_pyvista.helpers.streamlit_pyvista_logging import root_logger
from streamlit_pyvista.helpers.utils import (
    find_free_port,
    is_server_available,
    is_server_alive,
    wait_for_server_alive,
    ServerItem,
    with_lock,
)
from streamlit_pyvista.message_interface import (
    ServerMessageInterface,
    EndpointsInterface,
)

# logging.getLogger('werkzeug').disabled = True

runner_lock = threading.Lock()


class ServerManagerBase(ABC):
    """This class is the base for any ServerManager implementation"""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
    ) -> None:
        self.app = Flask(__name__)
        # register API endpoints
        self.app.add_url_rule(
            EndpointsInterface.InitConnection, "init_connection", self.init_connection
        )
        self.app.add_url_rule(
            ROOT_URL + EndpointsInterface.InitConnection,
            "init_connection",
            self.init_connection,
        )

        self.servers_running = []
        self.host = host
        self.port = port
        self.viewer_runner_script = None
        self.timeout = 120

        # Set up a scheduler used to periodically kill servers that are not in use
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self._lifecycle_task_kill_server,
            "interval",
            kwargs={"servers_running": self.servers_running},
            seconds=3 * 60,
            max_instances=3,
        )

        self.maximum_nbr_instances = 1
        update_cache()

        atexit.register(self._on_server_stop)

    @abstractmethod
    def init_connection(self) -> Response:
        """
        This function receive request of clients that require a trame server to display meshes. It's in this class that
        we need by any means start a trame server and get its endpoints
        Returns:
            Response: A response containing a json with all required endpoint for a MeshViewerComponent to work properly
        """
        pass

    def init_connection_with_trame(self, url):
        try:
            res = requests.get(f"{url}/init_connection").json()
        except Exception:
            return None
        return res

    def run_server(self):
        """Start the flask server and the scheduler"""
        self.scheduler.start()
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
        root_logger.info(f"Started Server Manager {self.port} Service")

    def _on_server_stop(self):
        """Function called when the manager is stopped that stop all managed trame servers and stop the scheduler"""
        for server in self.servers_running:
            if is_server_alive(server.host):
                try:
                    requests.get(
                        f"{server.host}{EndpointsInterface.KillServer}", timeout=1
                    )
                except (
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.ConnectionError,
                ):
                    pass
        self.scheduler.shutdown()
        update_cache()
        root_logger.info(f"Server Manager {self.port}  was successfully stopped")

    @staticmethod
    def _get_viewer_content_from_request(
        cur_req: Request,
    ) -> tuple[Optional[bytes], Optional[Union[str, Response]]]:
        """
        get the content of the viewer file passed over the http request
        Args:
            cur_req(Request):
                request to extract the content from
        Returns:
            tuple[Optional[bytes], Optional[str]]:
                Return a tuple (content, checksum) filled with None if any error happens
        """
        # Check that the request is a json and parse it
        if cur_req.is_json:
            req = json.loads(cur_req.json)
        else:
            r = make_response(
                {
                    "Invalid format": "init_connection expected a json with field 'Viewer' "
                },
                400,
            )
            return None, r
        c = req.get(ServerMessageInterface.Keys.Viewer, None)
        if c is None:
            r = make_response(
                {
                    "Viewer missing": "You should include the content of your viewer "
                    "class file in the init_connection request"
                },
                400,
            )
            return None, r
        c = base64.b64decode(c)
        checksum = hashlib.sha256(c).hexdigest()
        return c, checksum

    @staticmethod
    @abstractmethod
    def get_launch_path() -> str:
        """
        This function must be used to get the path to the file of the manager that will be launched
        Returns:
            str: the path to the file that launch the server
        """
        pass

    def _find_available_server(self, server_type: str) -> Optional[ServerItem]:
        """
        Check in the servers_running attribute if any server is there idling if it's the case it returns
        the address of this server
        Args:
            server_type(str):
                the type of the viewer, define by the checksum of .py file containing the viewer
        Returns:
            Optional[ServerItem]: The address of idling server, if none is found return None
        """
        dead_servers = []
        for server in self.servers_running:
            if not is_server_alive(f"{server.host}/index.html"):
                dead_servers.append(server)
                continue
            if server_type == server.type and is_server_available(server):
                self.servers_running.remove(server)
                return server
        for s in dead_servers:
            self._remove_and_kill_server(s)
        return None

    def _process_init_connection(
        self,
    ) -> Tuple[Optional[ServerItem], Union[Dict[str, str], Response]]:
        """
        This function provide basic function to process an init_connection request

        Returns:
             Tuple[Optional[ServerItem], Union[Dict[str, str], Response]]: A tuple with the server associated to this
             request and the dict mapping all endpoints of the server resulting from an init_connection call to the
             trame server. In addition, in case of error in the setup, the first element of the tuple is set to None
             and the second is the response that should be sent back to the client
        """
        # Check that the request is a json and parse it
        file_content, checksum_or_response = self._get_viewer_content_from_request(
            request
        )
        if file_content is None:
            return None, checksum_or_response
        checksum = checksum_or_response
        root_logger.debug("check if already running server")
        # Check if any server already running is available and if one was found use it and response with its endpoints
        available_server = self._find_available_server(checksum)
        root_logger.debug(f"check if already running server done => {available_server}")
        # If the maximum of instances is reached, delete the oldest one and create a new one
        if (
            len(self.servers_running) + (1 if available_server is not None else 0)
            >= self.maximum_nbr_instances
        ):
            if available_server is not None:
                self.servers_running.append(available_server)
            root_logger.debug("remove oldest server")
            self._remove_oldest_server()
            available_server = None
        if available_server is not None:
            root_logger.debug(
                f"Trame Server {available_server.host} was available and is used for a new request"
            )
            self.servers_running.append(available_server)
            res = self.init_connection_with_trame(available_server.host)
            if res is not None:
                res[ServerMessageInterface.Keys.Host] = (
                    f"{available_server.host}{EndpointsInterface.InitConnection}"
                )
                return None, make_response(res, 200)

            # If we reach this line it means that we couldn't connect to the trame sever properly hence we kill it
            # and let the function work as if no server was available
            self._remove_and_kill_server(available_server)
        root_logger.debug("finding free port")
        port = find_free_port()
        root_logger.debug(f"found free port: {port}")

        cache_entry = save_file_content(
            cache_id=f"{DEFAULT_CACHE_DIR}/{DEFAULT_VIEWER_CACHE_NAME}",
            content=file_content,
            cache_dir=DEFAULT_CACHE_DIR,
        )
        file_path = cache_entry["filename"]

        root_logger.debug(f"file_path: {file_path}")

        # Run the trame server in a new thread
        threading.Thread(target=run_trame_viewer, args=[port, file_path]).start()
        # Wait for server to come alive
        if not wait_for_server_alive(
            f"{EndpointsInterface.Localhost}:{port}", self.timeout
        ):
            return None, make_response(
                {
                    "Server timeout error": f"Unable to connect to Trame instance on port {port},\
                                                                     the server might have crashed"
                },
                400,
            )
        root_logger.debug("here")
        res = self.init_connection_with_trame(f"{EndpointsInterface.Localhost}:{port}")
        server = ServerItem(
            res[ServerMessageInterface.Keys.Host],
            checksum,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            file_path,
        )
        self.servers_running.append(server)

        return server, res

    def _remove_oldest_server(self):
        """
        Remove the oldest trame server running
        """
        sorted_dates = list(
            sorted(
                self.servers_running,
                key=lambda x: datetime.strptime(x.last_init, "%Y-%m-%d %H:%M:%S"),
            )
        )
        self._remove_and_kill_server(sorted_dates[0])

    def _remove_and_kill_server(self, server: ServerItem):
        """
        Take a server and send a signal to kill it and remove it from running server list

        Args:
            server (ServerItem): The server to remove
        """
        try:
            url = f"{server.host}/kill_server"
            if is_server_alive(url):
                requests.get(url, timeout=1)
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
        ):
            pass
        self.servers_running.remove(server)

    def _lifecycle_task_kill_server(
        self, servers_running: list[ServerItem]
    ) -> list[ServerItem]:
        """
        Task executed periodically by the scheduler to kill all unused server
        Args:
            servers_running(list[ServerItem]): A list of server currently running

        Returns:
            list[ServerItem]: The server that were killed
        """
        elements_to_remove = []
        for server in servers_running:
            if is_server_alive(server.host) and is_server_available(server):
                elements_to_remove.append(server)
        for el in elements_to_remove:
            self._remove_and_kill_server(el)

        root_logger.debug(
            f"Server Manager {self.port} lifecycle task killed the following servers: {elements_to_remove}"
        )
        update_cache()
        return elements_to_remove


def run_trame_viewer(server_port: int, file_path: str):
    """Launch a Trame server using python subprocess"""
    try:
        cmd = ["python3", file_path, "--server", "--port", str(server_port)]
        root_logger.debug(f"launch cmd: {cmd}")
        subprocess.run(
            ["python3", file_path, "--server", "--port", str(server_port)],
            # capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        error_message = f"""
            Command '{e.cmd}' returned non-zero exit status {e.returncode}.

            STDOUT:
            {e.stdout}

            STDERR:
            {e.stderr}

            Python Traceback:
            {traceback.format_exc()}
            """
        root_logger.error(f"Trame Server {server_port} crashed")
        root_logger.debug(f"Failed with the following error: {error_message}")


class ServerManager(ServerManagerBase):
    """Implementation of a ServerManagerBase to run trame viewer locally"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        super().__init__(host, port)
        root_logger.debug("server manager constructed")

    @with_lock(runner_lock)
    def init_connection(self) -> Response:
        root_logger.info("init_connection")

        serv, res_or_resp = self._process_init_connection()
        if serv is None:
            return res_or_resp

        return make_response(res_or_resp, 200)

    @staticmethod
    def get_launch_path():
        return os.path.abspath(__file__)


if __name__ == "__main__":
    # Add command line argument and support
    parser = argparse.ArgumentParser(description="Launch a trame server instance")
    # Add the port argument that allow user to specify the port to use for the server from command line
    parser.add_argument(
        "--port", type=int, default=9422, help="Specify the port of the server"
    )
    # Add --server flag that is used to specify whether to use the trame as only a server and block the
    # automatic open of a browser
    parser.add_argument(
        "--server",
        action="store_true",
        help="Specify if the trame is opened as a server",
    )
    args = parser.parse_args()
    server_manager = ServerManager(port=args.port)
    server_manager.run_server()
