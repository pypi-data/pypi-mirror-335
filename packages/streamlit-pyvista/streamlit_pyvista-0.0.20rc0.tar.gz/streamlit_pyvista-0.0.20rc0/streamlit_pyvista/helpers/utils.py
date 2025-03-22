import time
from dataclasses import dataclass
from functools import wraps

import requests

from streamlit_pyvista.message_interface import ServerMessageInterface, EndpointsInterface

time.time()


@dataclass
class ServerItem:
    """
    A class used to represent servers that managers instantiate

    Attributes:
    host (str): The host of the server.
    type (str): The type of the server. Default is None.
    path (str): The path of the server. Default is None.
    """
    host: str
    type: str = None
    last_init: str = None
    path: str = None


def with_lock(lock):
    def with_lock_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            lock.acquire()
            try:
                return func(*args, **kwargs)
            finally:
                lock.release()

        return wrapper

    return with_lock_decorator


def is_localhost(url: str) -> bool:
    """
    Check if the url is localhost or is remote
    Args:
        url(str): the url to check

    Returns:
        bool: True if the url is a localhost url, False otherwise
    """
    from urllib.parse import urlparse
    if not url.startswith("http"):
        url = "http://" + url
    parsed_url = urlparse(url)
    # Check if the hostname is localhost or 127.0.0.1
    return parsed_url.hostname in ('localhost', '127.0.0.1')


def replace_host(url: str, new_host: str) -> str:
    """
    Replace the host in a given URL with a new host.

    Args:
        url (str): The original URL.
        new_host (str): The new host to replace the old host.

    Returns:
        str: The URL with the host replaced.
    """
    from urllib.parse import urlparse, urlunparse
    parsed_url = urlparse(url)
    if not new_host.startswith("http"):
        new_host = "http://" + new_host
    new_host_parsed = urlparse(new_host)
    # Construct the new URL with the replaced host
    new_url = urlunparse((
        parsed_url.scheme if not new_host_parsed.scheme else new_host_parsed.scheme,
        new_host_parsed.netloc,
        new_host_parsed.path + parsed_url.path,
        parsed_url.params,
        parsed_url.query,
        parsed_url.fragment
    ))
    return new_url


def is_web_link(string: str) -> bool:
    """
    Check if the input is a link
    Args:
        string (str): string to check

    Returns:
        bool: True if the string is a url, False otherwise
    """
    import re
    # Regular expression pattern to match a typical web link
    web_link_pattern = r'^https?://.*$'

    return bool(re.match(web_link_pattern, string))


def find_free_port() -> int:
    """
    Find a free port on the local machine

    Returns:
        int: A free port
    """
    import socket
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def is_free_port(port: int, host: str = "localhost") -> bool:
    """
    Check if a given port is free or not

    Args:
        port (int): The port to check.
        host (str): The host. By default, "localhost".

    Returns:
        bool: True if the port is free, False otherwise.
    """
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except socket.error:
            return True


def is_server_available(server: ServerItem):
    """
    Check if the server is available by checking if the number of clients connected to the server is 0

    Args:
        server (ServerItem): The server to check

    Returns:
        bool: True if the server is available, False otherwise
    """
    import requests
    try:
        res = requests.get(f"{server.host}/nbr_clients")
        return int(res.json()["nbr_clients"]) == 0
    except Exception:
        return False


def is_server_alive(server_url: str, timeout: float = 10):
    """
    Check if the server is alive by making a request to the server

    Args:
        server_url (ServerItem): The server to check
        timeout (float): The timeout for the request. Default is 0.5.

    Returns:
        bool: True if the server is alive, False otherwise
    """
    import requests
    """ Try to make a request to the server and see if it responds to determine if he is alive """
    try:
        r = requests.get(server_url, timeout=timeout)
        if r.status_code == 500:
            return False

        return True
    except Exception:
        return False


def wait_for_server_alive(server_url: str, timeout: float = 2) -> bool:
    import time
    """
    Try to ping the server to see if it is up.
    Args:
        server_url(str): url of the server to wait.
        timeout(float): a timeout period.

    Returns:
        bool: True if the server is up, False if it timed out.
    """
    init_time = time.time()
    while not is_server_alive(server_url):
        if time.time() - init_time >= timeout:
            return False
    return True


def get_local_ip():
    import socket
    try:
        # Create a socket object and connect to an external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return f"Error: {e}"


def is_notebook() -> bool:
    """
    Detect if the code is being run in a jupyter notebook
    Returns:
        bool: True if the code is currently run in a juypter notebook, False otherwise
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def known_by_manager(host: str, trame_port: int):
    try:
        res = requests.get(host + EndpointsInterface.KnownByManager,
                           json={ServerMessageInterface.Keys.TramePort: trame_port})
    except Exception:
        return False

    if res.status_code != 200:
        return False

    return res.json()[ServerMessageInterface.Keys.Success]
