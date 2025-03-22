import base64
import json
import os
import subprocess
import threading
import time
import traceback
from typing import Type, Union, Optional

import requests
import streamlit as st
import streamlit.components.v1 as components
import validators

from streamlit_pyvista.helpers.cache import DEFAULT_CACHE_DIR
from streamlit_pyvista.helpers.streamlit_pyvista_logging import root_logger
from streamlit_pyvista.helpers.utils import (
    is_localhost,
    is_web_link,
    replace_host,
    is_server_alive,
    is_notebook,
    wait_for_server_alive,
    find_free_port,
)
from streamlit_pyvista.trame_viewers.trame_viewer import get_default_viewer_path
from .message_interface import ServerMessageInterface, EndpointsInterface
from .server_managers import ServerManagerBase, ServerManager


class MeshViewerComponent:
    """Streamlit component to display 3d mesh using pyvista and it's Trame backend"""

    def __init__(
        self,
        mesh_path: Union[str, list[str], None] = None,
        server_manager_url: str = "http://127.0.0.1:9422",
        setup_endpoint: str = EndpointsInterface.InitConnection,
        server_manager_class: Type[ServerManagerBase] = ServerManager,
        trame_viewer_class: Optional[str] = None,
    ):

        # If the user specified only the path of one file, transform it to an element in a list
        if isinstance(mesh_path, str):
            mesh_path = [mesh_path]

        self.manager = server_manager_class
        if trame_viewer_class is None:
            self.viewer = get_default_viewer_path()
        else:
            self.viewer = trame_viewer_class

        if not self._set_mesh_attributes(mesh_path):
            return

        root_logger.debug(f"Loaded sequence size: {self.sequence_size}")

        self.width = 1200
        self.height = 1000
        self.default_port = 9422
        self.server_url = server_manager_url
        self.server_timeout = 100
        self.manager_launch_timeout = 4
        self.error_during_setup = None
        self.max_attempts = 3

        # Set all attribute related to the dynamic endpoints settings.
        # Set the default required endpoints,
        # select mesh is used to ask the server to show a specific mesh and host is the host of the data rendering
        self.required_endpoints = [
            ServerMessageInterface.Keys.SelectMesh,
            ServerMessageInterface.Keys.UploadMesh,
            ServerMessageInterface.Keys.Host,
        ]
        # Dict that will contained value received for our endpoints. Init connection is the default endpoint to
        # request the server to give use all it's required endpoints
        self.endpoints = {
            ServerMessageInterface.Keys.InitConnection: setup_endpoint,
        }

        root_logger.debug(f"Setting up servers: {self.server_url}")

        # If the default server url is on localhost we launch the server manager locally
        if is_localhost(self.server_url):
            root_logger.debug(
                f"Server Manager url ({self.server_url}), a local instance is launched"
            )
            self._setup_server()

        root_logger.debug("Servers setup done")

        # Set up the endpoints
        if not self._setup_endpoints():
            root_logger.error("Couldn't setup the endpoints with the Trame server")
            return

        root_logger.info("Setting meshes")
        self.set_mesh()
        root_logger.info("Setting meshes: done")

        root_logger.info("MeshViewer Created")

    def _set_mesh_attributes(self, mesh_path: Optional[list[str]]) -> bool:
        if not self.check_valid_input_files(mesh_path):
            self.endpoints = None
            return False

        self.mesh_path = mesh_path
        if mesh_path is not None:
            self.sequence_size = len(mesh_path)
        else:
            self.sequence_size = 0
        return True

    @staticmethod
    def check_valid_input_files(list_of_path):
        """
        Take a list of paths and check that each path exists.

        Args:
            list_of_path (list[str]): The list of paths to check.

        Returns:
            bool: True if all files exist, False otherwise.
        """
        found_all = True
        for i in range(len(list_of_path)):
            if is_web_link(list_of_path[i]):
                if not validators.url(list_of_path[i]):
                    root_logger.error(f"The link {list_of_path[i]} is not valid")
                    found_all = False
                continue
            if not os.path.isabs(list_of_path[i]):
                list_of_path[i] = os.path.join(os.getcwd(), list_of_path[i])
            if not os.path.exists(list_of_path[i]):
                root_logger.error(f"The file {list_of_path[i]} does not exists")
                found_all = False
        return found_all

    def _setup_server(self, force_create_new_manager=False):
        """
        Launch a local server using python subprocess on another thread. If a Trame server isn't already running
        """
        if (
            is_server_alive(self.server_url, self.server_timeout)
            and not force_create_new_manager
        ):
            return

        trame_viewer_thread = threading.Thread(
            target=self._run_server_manager, args=(0, force_create_new_manager)
        )
        trame_viewer_thread.start()
        prev_url = self.server_url
        start_time = time.time()
        while (
            trame_viewer_thread.is_alive()
            and time.time() - start_time < self.manager_launch_timeout
        ):
            if prev_url != self.server_url:
                break

        root_logger.info("Local Server Manager is launched")
        root_logger.debug(
            f"Server Manager logs and trame server logs are available in a \
            log file in {os.path.join(os.getcwd(), DEFAULT_CACHE_DIR)}"
        )

    def wait_manager_alive(self):
        attempt = 0
        prev_serv = ""
        res = False

        while not res and prev_serv != self.server_url and attempt < self.max_attempts:
            prev_serv = self.server_url
            wait_for_server_alive(self.server_url, self.manager_launch_timeout)
            attempt += 1

    def _setup_endpoints(self, attempt=0):
        """
        Fill the endpoints dictionary with the info received from the server

        Returns:
            bool: True if the setup was successful, False otherwise.
        """
        if attempt >= self.max_attempts:
            self.error_during_setup = (
                "Tried to launch and setup endpoints with server_manager "
                "several time without success, it's likely due to"
                " a crash in the init_connection endpoints of the server_manager"
            )
            return False

        # If the server was launched locally, we need to wait for it to be up
        self.wait_manager_alive()
        with open(self.viewer, "rb") as f:
            c = f.read()
        base64_bytes = base64.b64encode(c)
        request_body = {
            ServerMessageInterface.Keys.Viewer: base64_bytes.decode("utf-8")
        }

        try:
            root_logger.debug(
                f"Request {self.server_url + self.endpoints[ServerMessageInterface.Keys.InitConnection]}"
            )

            res = requests.get(
                self.server_url
                + self.endpoints[ServerMessageInterface.Keys.InitConnection],
                json=json.dumps(request_body),
                timeout=self.server_timeout,
            )

        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            root_logger.error(
                f"Failed to establish a connection with the server {self.server_url}"
            )
            self.error_during_setup = (
                f"Failed to establish a connection with the server {self.server_url}"
            )
            return False

        root_logger.debug(f"Request result {res}")

        if res.status_code == 500:
            self._setup_server(force_create_new_manager=True)
            return self._setup_endpoints(attempt + 1)
        elif res.status_code != 200:
            self.error_during_setup = (
                "The response the server manager gave was not with status 200"
            )
            return False

        try:
            json_res = res.json()
        except json.JSONDecodeError:
            root_logger.error(
                "The init_connection request should have a json object as response"
            )
            self.error_during_setup = (
                "The init_connection request should have a json object as response"
            )
            return False

        root_logger.debug(
            f"The endpoint received by the server are the following : {json_res}"
        )
        # Check that all necessary endpoints where given in the request and fill the endpoints Dict
        for endpoint in self.required_endpoints:
            if endpoint not in json_res:
                root_logger.error(
                    f"The endpoint {endpoint} was not specified by the server"
                )
                self.error_during_setup = (
                    f"The endpoint {endpoint} was not specified by the server"
                )
                return False
            self.endpoints[endpoint] = json_res[endpoint]
        return True

    def _run_server_manager(self, attempt=0, force_create_new_manager=False):
        """
        Launch a Trame server using python subprocess
        """
        try:
            root_logger.info(
                f'launch: {["python3", self.manager.get_launch_path(), "--port", str(self.default_port)]}'
            )
            subprocess.run(
                [
                    "python3",
                    self.manager.get_launch_path(),
                    "--port",
                    str(self.default_port),
                ],
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

            root_logger.info(f"Failed with the following error: {error_message}")

            if "Address already in use" in e.stderr or force_create_new_manager:
                new_port = find_free_port()
                self.server_url = self.server_url.replace(
                    f"{self.default_port}", f"{new_port}"
                )
                self.default_port = new_port
                root_logger.debug(
                    f"The port was already in use, starting a new manager on port {self.default_port}"
                )
                self._run_server_manager(attempt + 1)
                return

            root_logger.error(
                "Tried to launch the Server Manager but got an unexpected error"
            )
            root_logger.debug(f"Failed with the following error: {error_message}")
            if attempt < self.max_attempts:
                time.sleep(2)
                self._run_server_manager(attempt + 1)

    def set_mesh(self, meshes: Union[list[str], str] = None):
        """
        Set the mesh viewed on the server by making a request.

        Args:
            meshes (list[str]|str): List of paths to the meshes to display.
        """

        if meshes is None:
            meshes = self.mesh_path
        else:
            if isinstance(meshes, str):
                meshes = [meshes]
            if not self._set_mesh_attributes(meshes):
                return

        if ServerMessageInterface.Keys.SelectMesh not in self.endpoints:
            return

        url = (
            self.endpoints[ServerMessageInterface.Keys.Host]
            + self.endpoints[ServerMessageInterface.Keys.SelectMesh]
        )
        data = {
            ServerMessageInterface.ReqSetMesh.MeshList: meshes,
            ServerMessageInterface.ReqSetMesh.NbrFrames: len(meshes),
            ServerMessageInterface.ReqSetMesh.Width: self.width,
            ServerMessageInterface.ReqSetMesh.Height: self.height,
        }

        try:
            headers = {"Content-Type": "application/json"}
            # Check in the response if any action is necessary such as make the iframe bigger or uploading files
            response = requests.post(
                url, data=json.dumps(data), headers=headers, timeout=self.server_timeout
            )
            resp_body = response.json()

            if response.status_code == 400:
                if ServerMessageInterface.RespSetMesh.Error in resp_body:
                    self.error_during_setup = resp_body
                    root_logger.error(
                        resp_body[ServerMessageInterface.RespSetMesh.Error]
                    )
            else:
                if ServerMessageInterface.RespSetMesh.RequestSpace in resp_body:
                    self.height = resp_body[
                        ServerMessageInterface.RespSetMesh.RequestSpace
                    ]
                elif ServerMessageInterface.RespSetMesh.RequestFiles in resp_body:
                    missing_files = resp_body[
                        ServerMessageInterface.RespSetMesh.RequestFiles
                    ]
                    root_logger.debug(
                        f"Trame server {self.endpoints[ServerMessageInterface.Keys.Host]} requested the following "
                        f"files : {missing_files}"
                    )
                    self._send_missing_files(missing_files)

        except requests.exceptions.JSONDecodeError:
            return
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            self.error_during_setup = (
                f"Couldn't connect to the server with url {url}, either the server "
                f"or the proxy crashed"
            )

    def _send_missing_files(self, missing_files: list[str]):
        """
        If the trame server cannot access every file that he was asked to display then we need to upload them to him

        Args:
            missing_files(list[str]): The list of file paths that couldn't be access by the server and that needs to be\
                sent to the server
        """
        for file, index in missing_files:
            request_body = {}
            if file in self.mesh_path:
                with open(file, "rb") as f:
                    content = f.read()
                base64_bytes = base64.b64encode(content)
                request_body[file] = (base64_bytes.decode("utf-8"), index)
                url = (
                    self.endpoints[ServerMessageInterface.Keys.Host]
                    + self.endpoints[ServerMessageInterface.Keys.UploadMesh]
                )
                headers = {"Content-Type": "application/json"}
                root_logger.debug(
                    f"Sent file with path {file} to {self.endpoints['host']}"
                )
                requests.post(
                    url,
                    data=json.dumps(request_body),
                    headers=headers,
                    timeout=self.server_timeout,
                )

    def show(self):
        """Render the streamlit component"""
        from . import REMOTE_HOST

        # The only scenario that leads to endpoints = None is if one of the file is not valid
        if self.endpoints is None:
            return st.error("Some files passed as argument does not exists")

        if self.error_during_setup is not None:
            return st.error(self.error_during_setup)

        root_logger.debug("start show()")
        headers = st.context.headers
        host = headers.get("Host") if not REMOTE_HOST and headers else REMOTE_HOST
        root_logger.debug(f"Host: {host}")
        if host and not is_localhost(host) and is_localhost(self.server_url):
            root_logger.debug(
                f"The host that the iframe should have is {host} and it "
                f"actually has {self.endpoints[ServerMessageInterface.Keys.Host]}"
            )
            iframe_host = replace_host(
                self.endpoints[ServerMessageInterface.Keys.Host], host
            )
        else:
            iframe_host = self.endpoints[ServerMessageInterface.Keys.Host]
        url = iframe_host + "/index.html"
        if is_notebook():
            from IPython.display import IFrame, display

            iframe = IFrame(src=url, width="100%", height=self.height)
            display(iframe)
        else:
            return components.iframe(url, height=self.height)
