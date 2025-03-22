import argparse
import ipaddress
import os
import subprocess
import threading
import traceback
from threading import Lock
from typing import Optional

import requests
from flask import request, make_response

from streamlit_pyvista import ROOT_URL
from streamlit_pyvista.helpers.streamlit_pyvista_logging import root_logger
from streamlit_pyvista.helpers.utils import (
    is_server_alive,
    wait_for_server_alive,
    ServerItem,
    with_lock,
)
from streamlit_pyvista.message_interface import (
    EndpointsInterface,
    ProxyMessageInterface,
    ServerMessageInterface,
)
from streamlit_pyvista.server_managers.server_manager import ServerManagerBase

runner_lock = Lock()


def run_proxy():
    def start(nbr_tries=0):
        try:
            subprocess.run(
                ["streamlit-pyvista-proxy", "run", "proxy"],
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
            root_logger.error("Proxy crashed")
            root_logger.debug(f"Failed with the following error: {error_message}")
            if nbr_tries < 0:
                start(nbr_tries + 1)

    threading.Thread(target=start, daemon=True).start()


class ServerManagerProxified(ServerManagerBase):
    """Implementation of ServerManagerBase that make use of a proxy for remote connection"""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        proxy_host: str = "127.0.0.1",
        proxy_port: int = 5000,
    ):
        super().__init__(host, port)

        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.base_url = ROOT_URL

    def _extract_proxy_host(self):
        """
        Extract the proxy host from the request headers.
        """
        # Identify host used to access the server
        self.proxy_host = request.headers.get("Host").split(":")
        # Extract only the hostname and use proxy port
        if len(self.proxy_host) > 1:
            self.proxy_host[1] = str(self.proxy_port)
            self.proxy_host = ":".join(self.proxy_host)
        else:
            self.proxy_host = self.proxy_host[0]
        root_logger.debug(f"self.proxy_host {self.proxy_host}")

    def _get_host_for_client(self, server_id: int) -> str:
        """
        Change the host's endpoint to use the proxy, check if the host is an ip
        or a domain to reply with the right host

        Args:
            server_id (int): The id of the server.

        Returns:
            str: The host for the client.
        """
        try:
            ipaddress.ip_address(self.proxy_host)
            host = f"{EndpointsInterface.Protocol}://{self.proxy_host}{self.base_url}/server/{server_id}"
        except ValueError:
            host = f"{EndpointsInterface.Protocol}://{self.proxy_host}{self.base_url}/server/{server_id}"

        root_logger.debug(f"host for client: {host}")
        return host

    @with_lock(runner_lock)
    def init_connection(self):

        # Get the host of the proxy
        self._extract_proxy_host()
        serv, res_or_resp = self._process_init_connection()

        root_logger.debug("here")

        if serv is None:
            return res_or_resp
        res = res_or_resp
        port = res[ServerMessageInterface.Keys.Host].split(":")[-1]
        # Add the new server to the proxy server list
        proxy_url = f"{EndpointsInterface.Localhost}:{self.proxy_port}"
        # Launch the proxy if it's not already running
        if not is_server_alive(proxy_url):
            run_proxy()
        if not wait_for_server_alive(proxy_url, timeout=self.timeout):
            return make_response(
                {
                    "Server Timeout Error": "Unable to connect to the proxy, it might have crashed"
                },
                400,
            )

        host_through_proxy = self.register_server_to_proxy(res["host"])
        if host_through_proxy is None:
            return make_response(
                {
                    "error": "An error occurred when trying"
                    " to register the trame server to the proxy"
                },
                400,
            )
        res[ServerMessageInterface.Keys.Host] = host_through_proxy
        serv.host = host_through_proxy
        root_logger.debug(
            f"Trame Server {port} was launched successfully and routed with the proxy with "
            f"id={res[ServerMessageInterface.Keys.Host].split('/')[-1]}"
        )
        root_logger.debug(f"init_connection res {res}")

        return make_response(res, 200)

    def register_server_to_proxy(self, host):
        try:
            proxy_res = requests.get(
                f"http://{self.proxy_host}{self.base_url}{EndpointsInterface.Proxy.UpdateAvailableServers}",
                json={
                    ProxyMessageInterface.Keys.Action: ProxyMessageInterface.Actions.Add,
                    ProxyMessageInterface.Keys.ServerURL: host,
                },
            )
            server_id = proxy_res.json()[ProxyMessageInterface.Keys.ServerID]
        except Exception as e:
            root_logger.error(e)
            return None

        return self._get_host_for_client(server_id)

    def _find_available_server(self, server_type: str) -> Optional[ServerItem]:
        if not is_server_alive(f"{EndpointsInterface.Localhost}:{self.proxy_port}"):
            run_proxy()

        return super()._find_available_server(server_type)

    def _remove_and_kill_server(self, server: ServerItem):
        root_logger.debug(f"_remove_and_kill_server: {server}")
        super()._remove_and_kill_server(server)
        payload = {
            ProxyMessageInterface.Keys.Action: ProxyMessageInterface.Actions.Remove,
            ProxyMessageInterface.Keys.ServerURL: server.host,
        }
        requests.get(
            f"{EndpointsInterface.Protocol}://{self.proxy_host}{self.base_url}"
            f"{EndpointsInterface.Proxy.UpdateAvailableServers}",
            json=payload,
        )

    @staticmethod
    def get_launch_path():
        return os.path.abspath(__file__)

    def _lifecycle_task_kill_server(self, servers_running):
        servers_killed = super()._lifecycle_task_kill_server(servers_running)
        # Complete the routine by notifying the proxy of all the server that needs to be unreferenced
        for server in servers_killed:
            payload = {
                ProxyMessageInterface.Keys.Action: ProxyMessageInterface.Actions.Remove,
                ProxyMessageInterface.Keys.ServerURL: server.host,
            }
            requests.get(
                f"{EndpointsInterface.Protocol}://{self.proxy_host}{self.base_url}"
                f"{EndpointsInterface.Proxy.UpdateAvailableServers}",
                json=payload,
            )

        return servers_killed


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
    server_manager = ServerManagerProxified(port=args.port)
    server_manager.run_server()
