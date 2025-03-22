import asyncio
import base64
import signal
import threading
from abc import ABC, abstractmethod
from types import FrameType
from typing import Optional
from multiprocessing import Process, Queue

# from more_itertools.recipes import flatten
import numpy as np
import pyvista as pv

# import validators
from aiohttp import web
from trame.app import Server
from trame.app import get_server
from trame.ui.vuetify3 import VAppLayout

from streamlit_pyvista.helpers.cache import save_mesh_content, DEFAULT_CACHE_DIR
from streamlit_pyvista.helpers.streamlit_pyvista_logging import root_logger

# from streamlit_pyvista.helpers.utils import is_web_link
from streamlit_pyvista.lazy_mesh import LazyMesh, LazyMeshList
from streamlit_pyvista.message_interface import (
    ServerMessageInterface,
    EndpointsInterface,
)

import streamlit_pyvista.helpers.cache

streamlit_pyvista.helpers.cache.cache_dir = DEFAULT_CACHE_DIR

SECOND = 1
ONE_MINUTE = 60 * SECOND


def success_cb(arg):
    root_logger.debug(f"The worker was successful {arg}")


def error_cb(arg):
    root_logger.error(f"The worker got an error {arg} {type(arg)}")


class TrameBackend(ABC):
    """A Trame server class that manage the view of a 3d mesh and its controls"""

    def __init__(
        self,
        plotter: Optional[pv.Plotter] = None,
        server: Optional[Server] = None,
        port: int = 8080,
        host: str = "0.0.0.0",
    ):
        """
        Initialize the trame server backend.

        Args:
            plotter (pv.Plotter, optional): The plotter object for visualization. Defaults to None.
            server (Server, optional): The server object for handling client connections. Defaults to None.
            port (int, optional): The port number for the server. Defaults to 8080.
            host (str, optional): The host address for the server. Defaults to "0.0.0.0".
        """

        root_logger.debug(f"creating trame backend {self}")
        self.shutdown_event = asyncio.Event()
        pv.OFF_SCREEN = True
        self.host = host
        self.port = port

        # Get a server if none was passed
        if server is None:
            self.server = get_server(port=self.port)
        else:
            self.server = server

        # Set mesh related attributes
        self.paths = None
        self.current_mesh = None
        self.warp_free_mesh = None
        self.cache_path = DEFAULT_CACHE_DIR
        self.state.start_computing_bounds = False

        # Set style attributes
        self.plotter_style = {"background-color": "black", "font-color": "white"}

        # Create a plotter and attributes related to it
        pl = self._setup_pl()
        self.pl = pl if plotter is None else plotter

        # Setup server lifecycle callback functions
        self.on_server_bind = self.server.controller.add("on_server_bind")(
            self.on_server_bind
        )
        self.on_client_exited = self.server.controller.add("on_client_exited")(
            self.on_client_exited
        )
        self.on_client_connected = self.server.controller.add("on_client_connected")(
            self.on_client_connected
        )
        self.on_server_exited = self.server.controller.add("on_server_exited")(
            self.on_server_exited
        )

        # Init the client counter to 1 at start to avoid the server to be concurrently defined as available.
        # The counter is decremented by 1 after 3 seconds
        self.client_counter = 1
        threading.Timer(3 * SECOND, self._client_counter_cb).start()
        self.stop_timer = threading.Timer(4 * ONE_MINUTE, self.request_stop)
        self.stop_timer.start()

        # Setup api endpoints
        self.api_routes = [
            web.post(EndpointsInterface.SelectMesh, self.change_mesh),
            web.get(EndpointsInterface.InitConnection, self.init_connection),
            web.post(EndpointsInterface.UploadMesh, self.upload_mesh),
            web.get(EndpointsInterface.ClientsNumber, self.client_number),
            web.get(EndpointsInterface.KillServer, self.kill_server),
        ]

        self.mesh_missing = None
        self.sequence_bounds = [0, 0]
        # Set state variables that need to exist before the ui is built
        self._setup_state()

        self.mesh_array: Optional[LazyMeshList] = None
        self.width = 800
        self.height = 900
        self.controller_height = 450

        self.finished_mesh_setup = False

        self.server.ui.clear()
        self.server.ui.clear_layouts()
        self.server.ui.flush_content()
        self.ui = self._build_ui()
        self.result_queue = Queue()
        self.async_process = Process(
            target=self.async_bound_compute, args=(self.result_queue,)
        )
        root_logger.debug("done")

    async def client_number(self, request):
        return web.json_response(
            {ServerMessageInterface.Keys.NumberClients: self.client_counter}, status=200
        )

    def _client_counter_cb(self):
        """
        Decrements the client counter by 1.

        This method is called to update the client counter when a client disconnects.
        """
        self.client_counter -= 1

    async def kill_server(self, request):
        """
        Stops the server and returns a JSON response indicating success.

        Args:
            request: The request object.

        Returns:
            A JSON response with a success message and a status code of 200.
        """
        self.client_counter = 0
        asyncio.get_running_loop().call_soon(
            asyncio.create_task, self.request_stop(force_stop=True)
        )
        return web.json_response(
            {
                ServerMessageInterface.Keys.Success: f"Trame Server {self.host}:{self.port} killed"
            },
            status=200,
        )

    def _setup_pl(self) -> pv.Plotter:
        """
        Set up the plotter with the specified styles and return it.

        Returns:
            pv.Plotter: The configured plotter object.
        """
        # Create the plotter and add its styles
        pl = pv.Plotter()
        pl.background_color = self.plotter_style["background-color"]
        pl.theme.font.color = self.plotter_style["font-color"]
        self.bounds_scalar = None
        self.scalar_bar_mapper = None
        return pl

    @abstractmethod
    def _setup_state(self):
        """Set up all the state variables to initial values"""
        self.server.state.number_mesh_loaded = 0

    def set_number_loaded_callback(self, num: int):
        self.state.number_mesh_loaded = num
        self.server.force_state_push("number_mesh_loaded")

    @property
    def state(self):
        return self.server.state

    @property
    def ctrl(self):
        return self.server.controller

    def _update_mesh_displayed_from_index(self, idx: int):
        """
        Update the mesh displayed in the plotter using its index in the sequence

        Args:
            idx (int): Index of the mesh to show
        """
        if self.mesh_array is not None:
            if idx < self.sequence_bounds[1]:
                self.warp_free_mesh = self.mesh_array[idx]
                self._replace_mesh_displayed(self.mesh_array[idx])

    def _handle_new_mesh_list(self, mesh_list: list[str]) -> list[tuple[str, int]]:
        """
        This function handles the loading of new mesh in the server

        Args:
            mesh_list (List[str]): the paths of the mesh

        Returns:
            List[Tuple[str, int]]: a list of mesh that couldn't be loaded with only their path or link
        """
        self.mesh_array = LazyMeshList(self.cache_path)
        # If the mesh is a sequence, then format its paths and load all element in the mesh array
        root_logger.info(f"adds {len(mesh_list)} entries")
        for path in mesh_list:
            root_logger.debug(f"adding {path}")
            self.mesh_array.append(path)
        root_logger.info(f"added {len(mesh_list)} entries")

        if self.mesh_array.missing_meshes:
            root_logger.warning(f"missing meshes {self.mesh_array.missing_meshes}")
        return self.mesh_array.missing_meshes

    async def change_mesh(self, request) -> web.Response:
        """
        This function is called when a request to '/select_mesh' is made

        Args:
            request: the request received

        Returns:
            web.Response: a http status 200 if there was no error, else a http status 400

        Note:
            This function require the request received to have a json body with the following fields:
                - mesh_list: the paths (or the link) of the mesh to load
                - width: the width of the plotter
                - height: the height of the plotter
                - nbr_frames: the number of frames in the sequence
        """
        request_body = await request.json()
        root_logger.debug(f"request_body {request_body}")

        # Retrieve information from the request
        self.paths = request_body.get(ServerMessageInterface.ReqSetMesh.MeshList, None)
        root_logger.info(f"self.paths len => {len(self.paths)}")

        self.width = request_body.get(
            ServerMessageInterface.ReqSetMesh.Width, self.width
        )
        self.height = request_body.get(
            ServerMessageInterface.ReqSetMesh.Height, self.height
        )
        self.sequence_bounds[1] = request_body.get(
            ServerMessageInterface.ReqSetMesh.NbrFrames, self.sequence_bounds[1]
        )
        root_logger.info(f"New request received with {self.mesh_array}")
        if self.paths is None:
            root_logger.error(
                f"Trame server running on {self.host}:{self.server.port}: No filepath found in the change mesh request"
            )
            return web.json_response(
                {"error": "No filepath found in the change mesh request"}, status=400
            )

        # Reset the viewer to an empty state
        self._clear_viewer()

        # Get the mesh and prepare it to be displayed
        self.mesh_missing = self._handle_new_mesh_list(self.paths)
        root_logger.debug(f"self.mesh_missing {self.mesh_missing}")
        if len(self.mesh_missing) > 0:
            root_logger.info(
                f"Missing mesh: {list(self.mesh_missing)}, request made to client"
            )
            return web.json_response(
                {ServerMessageInterface.RespSetMesh.RequestFiles: list(self.mesh_missing)},
                status=200,
            )

        root_logger.debug("self._update_viewer_for_new_meshes()")
        self._update_viewer_for_new_meshes()
        # If the height allocated by the streamlit component, ask for more space in the response of the request
        response_body = {}

        return web.json_response(response_body, status=200)

    def _fill_option_arrays(self):
        """
        Fills the option arrays for the Trame backend.

        This method prepares UI elements that depend on the mesh by populating the option arrays.
        It filters out options that start with "vtk" and inserts "None" as the first option.

        Returns:
            None
        """
        new_options = self.mesh_array[0].array_names.copy()
        new_options = list(filter(lambda x: not x.startswith("vtk"), new_options))

        self.state.options = new_options
        self.state.options.insert(0, "None")
        self.state.options_warp = new_options

    def _update_viewer_for_new_meshes(self):
        """
        Handles a new mesh request by replacing the current mesh with the first mesh in the mesh array.
        Updates UI elements that depend on the mesh and shows the new mesh in the viewers and its controls.
        """
        self.load_par()
        self._update_mesh_displayed_from_index(0)
        self.pl.reset_camera()
        self._fill_option_arrays()
        self.on_start_computing()
        self.bound_thread = threading.Thread(target=self._computes_bounds_scalar)

        self.bound_thread.start()

        self.ui = self._build_ui()
        root_logger.debug("_update_viewer_for_new_meshes: done")

    @abstractmethod
    def on_start_computing(self):
        pass

    def load_par(self):
        # from multiprocessing import Pool

        root_logger.debug(f"self.sequence_bounds {self.sequence_bounds}")
        from tqdm import tqdm

        root_logger.debug(f"load {len(self.mesh_array)} meshes")
        res = []
        for m in tqdm(self.mesh_array):
            res.append(m.load())
        root_logger.info(f"loaded {len(self.mesh_array)} meshes")
        self.mesh_array.sync_cache()

        # threading.Thread(target=self._computes_bounds_scalar).start()
        root_logger.debug("Finished the Process pool")

    def _load_all(self):
        for i in range(self.sequence_bounds[1]):
            self.mesh_array[i]

    def async_bound_compute(self, queue: Queue):
        import traceback

        try:
            self._computes_bounds_scalar()
            queue.put(("bounds", self.bounds_scalar))
        except Exception as e:
            error_msg = f"Error occurred: {str(e)}\n{traceback.format_exc()}"
            queue.put(("error", error_msg))
        root_logger.debug("done")

    async def upload_mesh(self, request) -> web.Response:
        """
        This function is called when a request to '/upload_mesh' is made

        Args:
            request: The request object containing the mesh data.

        Returns:
            web.Response:A JSON response indicating the success of the upload.
        """
        request_body = await request.json()
        for key, (encoded_content, index) in request_body.items():
            content = base64.b64decode(encoded_content)
            loc = save_mesh_content(content, f"{self.cache_path}/{key}")
            self.mesh_array[index] = LazyMesh(loc[0], loc[1])
            self.mesh_missing.remove((key, index))

        if self.mesh_missing is None or len(self.mesh_missing) == 0:
            self._update_viewer_for_new_meshes()

        return web.json_response(
            {ServerMessageInterface.Keys.Success: "Mesh uploaded successfully"},
            status=200,
        )

    def _compute_field_interval(self, field: str = None) -> tuple[float, float]:
        """
        Compute the min and max of a field of vector over all it's frame ot get the all-time min and max to get
        the upper and lower bound of the scalar bar.

        Args:
            field (str): the field you want to compute the bounds

        Returns:
            Tuple[float, float]: it returns a tuple with the min and max
        """
        # If the field is None get the default field on which to compute the min and max
        if field is None or field == "None":
            field = self.state.options[1]
        # Loop over all the images and find the max of the array and the min
        max_bound = -np.inf
        min_bound = np.inf
        for i in range(len(self.mesh_array)):
            try:
                arr = self.mesh_array[i].get_array(field)
            except KeyError:
                continue
            if len(arr) == 0 or isinstance(arr[0], str):
                continue
            l_max = arr.max()
            l_min = arr.min()

            if l_max > max_bound:
                max_bound = l_max
            if l_min < min_bound:
                min_bound = l_min
        return min_bound, max_bound

    def _computes_bounds_scalar(self):
        """Compute the bounds of all the scalars of the mesh and store it in an attribute
        to avoid doing all the computation everytime a bar is shown"""
        self.state.start_computing_bounds = True

        if self.state.options is None:
            self.state.start_computing_bounds = False
            return
        # Store bounds and mapper for all the fields available except "None" which is the first one of the options array
        self.bounds_scalar = {}
        # We don't need to take the first option since we manually added it earlier with a `None`

        for field in self.state.options[1:]:
            self.bounds_scalar[field] = self._compute_field_interval(field)
        self.state.start_computing_bounds = False
        self.on_finish_computing()

    @abstractmethod
    def on_finish_computing(self):
        pass

    @abstractmethod
    def _replace_mesh_displayed(self, new_mesh: pv.DataSet):
        """
        Change the mesh displayed in the plotter and its related data
        Args:
            new_mesh (pv.DataSet): the new mesh to display
        """
        pass

    @abstractmethod
    def _clear_viewer(self):
        """Reset the viewer and its related attribute to an empty viewer"""
        self.bounds_scalar = None
        self.state.mesh_representation = None

    @abstractmethod
    def _build_ui(self) -> VAppLayout:
        """
        Build all the ui frontend with all different components

        Returns:
            VAppLayout: a VAppLayout for the server
        """
        pass

    def on_server_bind(self, wslink_server):
        """
        When the server is bind, add api endpoint to it
        Args:
            wslink_server: the socket manager of the server
        """
        wslink_server.app.add_routes(self.api_routes)

    def on_client_exited(self):
        """
        Handles the event when a client exits.

        Decreases the client counter and logs the event. If there are no more clients connected,
        it prints a message indicating that a client disconnected.
        """
        self.client_counter -= 1
        root_logger.debug(
            f"A client disconnected from Trame server {self.host}:{self.port}, there are {self.client_counter} "
            f"clients connected"
        )

    def on_client_connected(self):
        """
        This method is called when a client connects to the Trame server.
        It increments the client counter and logs the connection details.
        """
        self.client_counter += 1
        root_logger.debug(
            f"A client connected to Trame server {self.host}:{self.port}, there are {self.client_counter} "
            f"clients connected"
        )

    def on_server_exited(self, **kwargs):
        """
        Callback function called when the server has exited.
        """
        root_logger.debug(
            f"Trame server {self.host}:{self.port} has exited successfully"
        )

    async def init_connection(self, request) -> web.Response:
        """
        Base api endpoint on '/init_connection' to inform the client of all the endpoints available and their locations.

        Args:
            request: the request made to this endpoint

        Returns:
            web.Response: a json with all information about endpoints required and a success status 200
        """
        response_body = {
            ServerMessageInterface.Keys.SelectMesh: EndpointsInterface.SelectMesh,
            ServerMessageInterface.Keys.UploadMesh: EndpointsInterface.UploadMesh,
            ServerMessageInterface.Keys.Host: f"{EndpointsInterface.Localhost}:{self.server.port}",
        }
        root_logger.debug(
            f"Trame server {self.host}:{self.port} initialized connection with a client"
        )
        return web.json_response(response_body, status=200)

    async def start(self):
        """
        Starts the Trame server and waits for it to finish.
        """
        root_logger.info(f"Trame server running on {self.host}:{self.server.port}")
        await self.server.start(exec_mode="task", thread=True)
        # await self.shutdown_event.wait()

    async def request_stop(self, force_stop: bool = False):
        """
        Stops the server if there are no active clients, otherwise schedules a delayed call to stop.

        If there are no active clients connected to the server, the server is stopped immediately and the
        `shutdown_event` is set. Otherwise, a delayed call to `request_stop` is scheduled using `threading.Timer`
        and `asyncio.get_running_loop().call_soon(asyncio.create_task, self.request_stop())`.

        Args:
            force_stop (bool): Force the request to immediately stop the server
        """

        root_logger.debug("request stop called")
        if self.client_counter == 0 or force_stop:
            root_logger.debug(f"The Trame server {self.server.port} is about to stop")
            self.stop_timer.cancel()
            await self.server.stop()
            self.shutdown_event.set()
        else:
            if self.stop_timer.is_alive():
                self.stop_timer.cancel()
            self.stop_timer = threading.Timer(
                2 * ONE_MINUTE, lambda: self.run_async_function(self.request_stop)
            )
            self.stop_timer.start()

    def run_async_function(self, async_func):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(async_func())
        loop.close()

    def signal_handler(self, sig: int, frame: FrameType):
        """
        Handles the specified signal and initiates the shutdown process.

        Args:
            sig (int): The signal number.
                       frame (FrameType): The current stack frame.
        """
        root_logger.debug(f"Received signal {self} {sig}. Shutting down...")
        asyncio.create_task(self.request_stop())

    async def run(self):
        """
        Runs the Trame server.

        This method sets up signal handlers for interrupt and termination signals,
        and then starts the Trame server
        """
        # Set up signal handlers
        root_logger.debug("run")
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self.signal_handler)

        try:
            await self.start()
        finally:
            root_logger.info(f"Trame server on {self.host}:{self.server.port} stopped")
