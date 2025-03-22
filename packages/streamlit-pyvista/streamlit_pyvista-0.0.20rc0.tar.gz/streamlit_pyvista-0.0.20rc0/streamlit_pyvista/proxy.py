import os.path
from typing import Optional, Any

from flask import Flask, request
from flask_sock import Sock
import requests
from websocket import create_connection
import threading
import simple_websocket

from streamlit_pyvista import ROOT_URL
from streamlit_pyvista.helpers.streamlit_pyvista_logging import root_logger

app = Flask(__name__)
sock = Sock(app)

available_servers = []
base_url = ROOT_URL


def get_proxy_launch_path():
    return os.path.abspath(__file__)


@app.route(
    f"{base_url}/server/<server_id>/<path:path>",
    methods=["GET", "POST", "PUT", "DELETE"],
)
def proxy(server_id, path):
    """
    Main route of the proxy. This route simply forward the request to and return the result

    Args:
        server_id: id of the server, it will be looked in the available_servers map
        path: Path of the request to make to the server

    Returns:
         Response of the target server to the request
    """

    root_logger.info(f"server_id={server_id} path={path}")
    if path == "ws":
        # In case websocket are requested pm classical http just return 200
        raise
        return 200

    if path == "init_connection":
        root_logger.debug(
            f"Proxy - Start connection between server {server_id} and client"
        )

    # This route is for HTTP requests
    method = request.method
    # Save headers
    headers = {key: value for key, value in request.headers}
    # Save request data
    data = request.get_data()

    # Check if the server_id is valid
    server_id = int(server_id)
    if server_id >= len(available_servers) or available_servers[server_id] is None:
        root_logger.debug(
            f"Proxy - Request to {base_url}/server/{server_id}/{path}: The server id {server_id} is not valid,\
            it is either too big or belong to a server previously deleted"
        )
        return {
            "error": f"invalid server id, {server_id} is not recognized (available={available_servers})"
        }, 404
    # Make request to the target server
    url = f"{available_servers[server_id]}/{path}"
    try:
        root_logger.info(f"Making request {method} {url} {headers} {type(data)}")
        response = requests.request(
            method, url, headers=headers, data=data, timeout=120
        )
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        root_logger.error(f"THE PROXY COULDNT MAKE THE REQUEST; RETURNING 500; {e}")
        # Unregister the server from the proxy since it is dead
        available_servers[server_id] = None
        return "", 500

    if response.status_code != 200:
        root_logger.debug(f"request was server_id={server_id} path={path}")
        root_logger.error(response.content)

    # return the response of the server
    root_logger.debug(f"request was server_id={server_id} path={path}")
    # root_logger.debug(response.content)
    root_logger.debug(response.status_code)
    root_logger.debug(response.headers.get("Content-Type"))
    return (
        response.content,
        response.status_code,
        {"Content-Type": response.headers.get("Content-Type")},
    )


def find_available_index(candidate_list: list[Optional[Any]]) -> int:
    """
    Get the first occurrence of None in a list, if there is no None existing, it extends the list by one and insert
    a None at this spot

    Args:
        candidate_list(list[Optional[Any]]):
            the list were we want to find a free spot
    Returns:
        int: the first index where None is found, if list doesn't contain any None, extends it by one
    """

    root_logger.debug(f"candidate_list={candidate_list}")

    for i in range(len(candidate_list)):
        if candidate_list[i] is None:
            return i
    candidate_list.append(None)
    return len(candidate_list) - 1


@app.route(
    f"{base_url}/update_available_servers", methods=["GET", "POST", "PUT", "DELETE"]
)
def update_available_servers():
    """
    This route is used by a server manager to update the available_servers map by adding or removing servers

    Returns:
        A response containing information about the action taken. If a server was added,\
        add to the response the associated id of the server
    """
    re = request.json

    root_logger.debug(f"request={re}")

    if "server_url" not in re:
        return (
            {
                "error": 'Please specify the server you want to affect by adding\
             a "server_url" field to the json of the request '
            },
            400,
        )

    resp = {}
    # ------------------------ ADD CASE ------------------------
    if re["action"] == "add":
        # Check that the server is not already in the map to avoid having multiple times the same server
        if re["server_url"] not in available_servers:
            # Set the server id
            resp["server_id"] = find_available_index(available_servers)
            # Populate the available_servers map with the new key value pair
            available_servers[resp["server_id"]] = re["server_url"]
            root_logger.debug(
                f"Proxy - Added the server {re['server_url']} accessible with id {resp['server_id']}"
            )
        else:
            return {"message": f"Server {re['server_id']} already exists"}, 400

    # ------------------------ REMOVE CASE ------------------------
    elif re["action"] == "remove":
        # Look for the url in the list en replace it with None
        if re["server_url"] in available_servers:
            index = available_servers.index(re["server_url"])
            available_servers[index] = None
            root_logger.debug(
                f"Proxy - Successfully removed server with host {re['server_url']} in the proxy"
            )
    else:
        return {
            "error": f"The action {re['action']} was not recognized, please choose between \"remove\" and \"add\""
        }, 400

    return {
        "message": f"Server {re['server_url']} updated succesfully with action {re['action']}"
    } | resp, 200


def forward_client_to_target(ws, target_ws):
    """
    This function forward the websocket of the client to the server

    Args:
        ws: client's websocket
        target_ws: server's websocket
    """
    root_logger.debug(f"ws={ws} target_ws={target_ws}")

    while ws.connected and target_ws.connected:
        try:
            client_data = ws.receive()
            target_ws.send(client_data)
            # root_logger.debug(f"client_data={client_data}")
        except simple_websocket.errors.ConnectionClosed:
            root_logger.error("failed proxy ws")
            break


def forward_target_to_client(ws, target_ws):
    """
    This function forward the websocket of the server to the client

    Args:
        ws: server's websocket
        target_ws: client's websocket
    """

    root_logger.debug(f"ws={ws} target_ws={target_ws}")

    while target_ws.connected and ws.connected:
        try:

            target_data = target_ws.recv()
            ws.send(target_data)
            # root_logger.debug(f"target_data={target_data}")
        except simple_websocket.errors.ConnectionClosed as e:
            root_logger.error(f"failed proxy ws: {e}")
            break


@sock.route(f"{base_url}/server/<server_id>/ws")
def echo(ws: simple_websocket.ws.Server, server_id):
    """
    This route connect the websocket from the client and the server together and launch forwarding function\
    in both direction

    Args:
        ws: the websocket of the client
        server_id: the id of the server it tries to communicate with

    """
    # If the server_id does not exist return

    root_logger.debug(f"ws={ws} server_id={server_id}")

    server_id = int(server_id)
    if server_id >= len(available_servers) or available_servers[server_id] is None:
        root_logger.debug(
            f"Proxy - Request to {base_url}/server/{server_id}/ws: The server id {server_id} is not valid, it is\
             either too big or belong to a server previously deleted"
        )
        return

        # Create the websocket with the target server
    target_ws = create_connection(
        f"ws://{available_servers[server_id].split('//')[1]}/ws"
    )

    # Create separate threads for forwarding messages
    client_to_target_thread = threading.Thread(
        target=forward_client_to_target, args=(ws, target_ws)
    )
    target_to_client_thread = threading.Thread(
        target=forward_target_to_client, args=(ws, target_ws)
    )

    # Start the threads
    client_to_target_thread.start()
    target_to_client_thread.start()
    root_logger.debug(
        f"Proxy - Opened websocket connection between client and {available_servers[server_id]}"
    )
    # Wait for threads to finish
    client_to_target_thread.join()
    target_to_client_thread.join()
    # Close the websockets
    ws.close()
    target_ws.close()
    root_logger.debug(
        f"Proxy - Closed websocket connection with {available_servers[server_id]}"
    )


def launch_proxy():
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    launch_proxy()
