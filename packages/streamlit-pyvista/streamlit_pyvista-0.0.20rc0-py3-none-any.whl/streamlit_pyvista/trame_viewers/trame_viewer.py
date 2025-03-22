import argparse
import asyncio
import os
import threading
import time
from typing import Optional

import pyvista as pv
from pyvista.trame.ui import plotter_ui
from trame.app import Server
from trame.decorators import TrameApp, change, controller
from trame.ui.vuetify3 import VAppLayout
from trame.widgets import html
from trame.widgets import vuetify3 as vuetify

from streamlit_pyvista.helpers.streamlit_pyvista_logging import root_logger
from streamlit_pyvista.trame_viewers.trame_backend import TrameBackend

MILLISECOND = 1
SECOND = 1000 * MILLISECOND


def get_default_viewer_path():
    return os.path.abspath(__file__)


@TrameApp()
class TrameViewer(TrameBackend):
    """
    This class is the main class of the trame viewer. It is used to display a mesh and its associated vector field
    """

    def __init__(
        self,
        plotter: Optional[pv.Plotter] = None,
        server: Optional[Server] = None,
        port: int = 8080,
        host: str = "0.0.0.0",
    ):
        """
        Initialize the TrameViewer object.

        Args:
            plotter (Optional[pv.Plotter]): A PyVista Plotter object. If provided, the TrameViewer will use this plotter
                for rendering.
            server (Optional[Server]): A Trame Server object. If provided, the TrameViewer will use this server
                for serving the application.
            port (int): The port number to use for the server. Default is 8080.
            host (str): The host address to bind the server to. Default is "0.0.0.0".
        """
        root_logger.debug("Init start")
        TrameBackend.__init__(self, plotter, server, port, host)
        self.state.slider_playing = False
        self.prev_orig = False

        self._setup_timer()
        self.loop = None
        root_logger.debug("Init done")

    def _setup_timer(self):
        """Set up the timer callback and timeout"""
        self.default_timer_timeout = 300 * MILLISECOND
        self.state.timer_timeout = self.default_timer_timeout
        self.timer = threading.Thread(target=self._timer_callback)

    def _setup_state(self):
        """Set up all the state variables to initial values"""
        self.state.is_full_screen = False
        self.state.mesh_representation = (
            self.state.options[0] if self.state.options is not None else None
        )
        self.state.warped_field = None
        self.state.original_resolution = False
        self.state.can_toggle_resolution = True

        # Option's dropdown
        self.state.options = [None]
        self.state.options_warp = [None]

        # Inputs
        self.state.warp_input = 0
        self.state.wireframe_on = False
        self.state.slider_value = 0
        self.state.play_pause_icon = "mdi-play"
        self.state.is_ready = False

    def _timer_callback(self):
        """This function is called on all timer tick and update the mesh viewed to animate a sequence of mesh
        playing"""

        # The animation needs to stop when the server stop or if the animation was paused by the user
        while self.state.slider_playing and self.server.running:
            # Increment the counter while keeping it within the bound of the mesh sequence
            self.state.slider_value = (
                self.state.slider_value + 1
            ) % self.sequence_bounds[1]
            # Call function on the main thread using thread safe method to update the server states and ui
            self.loop.call_soon_threadsafe(self.server.force_state_push, "slider_value")
            self.loop.call_soon_threadsafe(
                self._update_mesh_displayed_from_index, self.state.slider_value
            )

            time.sleep(self.get_sanitized_timer())
        # After the animation was stopped, reset the timer
        self.timer = threading.Thread(target=self._timer_callback)

    def get_sanitized_timer(self):
        if self.state.timer_timeout == "":
            return self.default_timer_timeout / SECOND
        timeout_ms = int(self.state.timer_timeout)
        return min(max(100 * MILLISECOND, timeout_ms), 2 * SECOND) / SECOND

    @change("mesh_representation")
    def _update_mesh_representation(self, mesh_representation, **kwargs):
        """This function is automatically called when the state 'mesh_representation' is changed.
        This state is used to determine which vector field is shown"""
        # Remove the scalar bar representing the last vector field shown
        self._clear_scalar_bars()

        # Replace the string input "None" with None
        if mesh_representation == "None":
            self.state.mesh_representation = None

        # Set all element of the mesh sequence with the same field shown
        for i in range(self.sequence_bounds[1]):
            if self.mesh_array is not None:
                self.mesh_array[i].set_active_scalars(self.state.mesh_representation)

        # Update ui elements
        self._update_mesh_displayed_from_index(self.state.slider_value)

    @change("wireframe_on")
    def _update_wireframe_on(self, **kwargs):
        """This function is automatically called when the state 'wireframe_on' is changed.
        This state is used to store whether we should show the wireframe of the mesh or the plain mesh.
        """
        self._replace_mesh_displayed(self.current_mesh)

    @change("original_resolution")
    def _update_original_resolution(self, **kwargs):
        if (
            self.mesh_array is None
            or self.state.slider_value >= self.sequence_bounds[1]
        ):
            return
        self.mesh_array.set_show_decimated(not self.state.original_resolution)
        if self.state.original_resolution:
            self._replace_mesh_displayed(self.mesh_array[self.state.slider_value])
        else:
            self._update_mesh_displayed_from_index(self.state.slider_value)

    @change("slider_value")
    def _slider_value_change(self, slider_value, **kwargs):
        """This function is automatically called when the state 'slider_value' is changed.
        This state is used to store the frame to actually displayed in a sequence."""
        self._update_mesh_displayed_from_index(int(slider_value))
        self.state.warp_input = 0

    def _update_mesh_displayed_from_index(self, idx: int):
        super()._update_mesh_displayed_from_index(idx)
        if self.mesh_array is None:
            return

    def _clear_scalar_bars(self):
        """Remove all the scalar bars shown on the plotter"""
        if self.pl is None:
            return
        bar_to_remove = [key for key in self.pl.scalar_bars.keys()]
        [self.pl.remove_scalar_bar(title=key) for key in bar_to_remove]

    def _clear_viewer(self):
        """Reset the viewer and its related attribute to an empty viewer"""
        super()._clear_viewer()
        self._clear_scalar_bars()
        self.state.slider_value = 0
        self.state.original_resolution = False
        self.state.slider_playing = False
        self.state.wireframe_on = False

    def _replace_mesh_displayed(self, new_mesh: pv.DataSet):
        """
        Change the mesh displayed in the plotter and its related data

        Args:
            new_mesh (pv.DataSet): the new mesh to display
        """
        if new_mesh is None:
            return

        # set custom style
        kwargs_plot = {}
        if self.state.wireframe_on:
            kwargs_plot["style"] = "wireframe"

        # update mesh and set its active scalar field, as well as adding the scalar bar
        self.current_mesh = new_mesh

        # Set the active scalar and create it's scalar bar if it does not exist
        self.current_mesh.set_active_scalars(self.state.mesh_representation)
        self.pl.mapper = self._show_scalar_bar(self.state.mesh_representation)

        # Replace actor with the new mesh (automatically update the actor because they have the same name)
        self.pl.add_mesh(
            self.current_mesh,
            style="wireframe" if self.state.wireframe_on else None,
            name="displayed_mesh",
            show_scalar_bar=True,
            scalar_bar_args={"mapper": self.pl.mapper},
        )

        self.state.can_toggle_resolution = not self.mesh_array.has_decimated_version(
            self.state.slider_value
        )

        self.pl.render()

    def on_start_computing(self):
        self.loop = asyncio.get_event_loop()

    def on_finish_computing(self):
        self.state.is_ready = True
        self.loop.call_soon_threadsafe(self.server.force_state_push, "is_ready")
        self.loop.call_soon_threadsafe(
            self._update_mesh_displayed_from_index, self.state.slider_value
        )

    def _show_scalar_bar(self, field: str = None):
        """
        Show the scalar bar associated with the field
        Args:
            field (str): The associated field of the bar that you want to show

        """
        if self.mesh_array is None:
            return

        # If the field is not specified try to get the actual field displayed in the plotter
        if field is None:
            field = self.state.mesh_representation
        if field is None:
            return

        # Get the bounds of the bar or compute it if it does not exist
        if self.bounds_scalar is None and not self.start_computing_bounds:
            self._computes_bounds_scalar()

        # Create the pyvista scalar bar
        bounds = self.bounds_scalar.get(field, None)
        if bounds is not None:
            self.pl.mapper.lookup_table.SetTableRange(bounds[0], bounds[1])
            self.pl.add_scalar_bar(self.state.mesh_representation)

        # Return the mapper to display the good max and min value on the bar
        return self.pl.mapper

    def _update_ui(self):
        """Force to redraw the ui"""
        if (
            self.current_mesh is not None
            and self.current_mesh.active_scalars is not None
        ):
            self.pl.remove_scalar_bar()
        self.ui = self._build_ui()

    def _option_dropdown(self):
        """
        This function generate a dropdown to select which field is displayed

        Returns:
            The ui element displaying the mesh_representation dropdown
        """
        return vuetify.VSelect(
            v_model=("mesh_representation", "None"),
            items=("options", self.state.options),
            label="Representation",
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
            disabled=("slider_playing | !is_ready",),
            raw_attrs=['data-testid="representation_dropdown"'],
        )

    def _build_slider(self):
        """
        This function build the ui component containing the slider to select the frame displayed

        Returns:
            A row containing a play-pause button and a slider
        """
        row = html.Div(
            style="display:flex;justify-content:center;align-content:center;gap:20px;"
        )
        with row:
            with vuetify.VBtn(
                icon=True,
                click=self._play_button,
                raw_attrs=['data-testid="play_sequence_button"'],
            ):
                vuetify.VIcon("{{ play_pause_icon }}")
            html.Div("{{ slider_value }}", raw_attrs=['data-testid="slider_value"'])
            vuetify.VSlider(
                ref="slider",
                label="",
                min=self.sequence_bounds[0],
                max=self.sequence_bounds[1] - 1,
                v_model=("slider_value", 8),
                step=1,
                raw_attrs=['data-testid="sequence_slider_component"'],
            )
        return row

    @controller.set("play_button")
    def _play_button(self):
        """This function is called the play-pause button of the slider is played and manage the state
        of the timer that updates the frame displayed in a periodic manner."""
        if self.sequence_bounds[1] <= 1:
            root_logger.error(
                "Impossible to start the sequence since it's a unique mesh"
            )
            return

        # Invert the state of the play button and if it's playing start the timer updating frame at a fixed interval
        self.state.slider_playing = not self.state.slider_playing

        if self.state.slider_playing and not self.timer.is_alive():
            self.state.play_pause_icon = "mdi-pause"
            self._store_mesh_list_states()
            self.loop = asyncio.get_event_loop()
            self.timer.start()
        else:
            self.state.play_pause_icon = "mdi-play"
            self._restore_mesh_list_states()
        root_logger.debug(
            f"Trame server running on {self.host}:{self.server.port}: The play button is {self.state.slider_playing}"
        )

    def _store_mesh_list_states(self):
        self.prev_orig = self.state.original_resolution

    def _restore_mesh_list_states(self):
        self.state.original_resolution = self.prev_orig

    def _build_mesh_control_layout(self):
        """
        This function return all the control part of the ui.

        Returns:
            A vuetify component representing all the control layout

        Note:
            The ui generated by this class is composed of:
                - The dropdown to select the vector field to display
                - The warp control
                - The slider controller
                - other various control

        """
        layout = html.Div()
        with layout:
            with vuetify.VRow(dense=True):
                # If there are options show the dropdown
                if self.state.options[0] is not None and len(self.state.options) > 1:
                    self._option_dropdown()
            vuetify.VCheckbox(
                v_model=("wireframe_on",),
                label="Wireframe on",
                id="wireframe_checkbox",
                disabled=("slider_playing",),
                raw_attrs=['data-testid="checkbox_wireframe"'],
            )
            with vuetify.VTooltip(
                text="Check to have the version with full resolution. The checkbox might be disabled if the "
                "mesh is small enough to be always displayed without decimation"
            ):
                with vuetify.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        v_bind="props",
                        on_icon="mdi-account-check",
                        off_icon="mdi-account-check-outline",
                    ):
                        vuetify.VCheckbox(
                            label="See mesh with its original resolution",
                            id="original_res_checkbox",
                            v_model=("original_resolution",),
                            classes="mx-1",
                            disabled=("can_toggle_resolution || slider_playing",),
                            raw_attrs=['data-testid="decimation_checkbox"'],
                        )

            # If the viewer display a sequence of mesh show the slider
            if self.sequence_bounds[1] > 1:
                vuetify.VTextField(
                    v_model=("timer_timeout", 250),
                    type="number",
                    label="Enter the time to wait between each frame in ms between 100 to 2000",
                    outlined=True,
                    disabled=("slider_playing",),
                )
                self._build_slider()
        return layout

    def _build_ui(self):
        """
        Build all the ui frontend with all different components

        Returns:
            a VAppLayout for the server
        """
        with VAppLayout(self.server) as layout:
            with layout.root:
                with html.Div(style=f"height: {self.height}px ;width:100%"):
                    with html.Div(
                        ref="container",
                        style=f"height:{self.height - self.controller_height}px;padding: 0;",
                    ):
                        # Create the plotter section
                        with vuetify.VCol(style="height:100%;padding: 0;"):
                            # If the slider is playing we force the app to use remote rendering to avoid bug
                            # with local rendering
                            if self.state.slider_playing:
                                plotter_ui(
                                    self.pl,
                                    default_server_rendering=True,
                                    mode="server",
                                    style="width: 100%; height:100%;background-color: black;",
                                )
                            else:
                                plotter_ui(
                                    self.pl,
                                    default_server_rendering=True,
                                    style="width: 100%; height:100%;background-color: black;",
                                )
                    with html.Div(style="height: 30px;"):
                        html.H3(
                            "You see the decimated version of the mesh",
                            v_show=(
                                "!original_resolution && " "!can_toggle_resolution",
                            ),
                        )
                    with html.Div(style="height: 30px;"):
                        html.H4(
                            (
                                "Mesh are still loading. You cannot select a field while",
                                "all the mesh are not properly loaded",
                            ),
                            v_show=("!is_ready",),
                        )

                    with vuetify.VCol(
                        style=f"height:{self.controller_height}px;padding: 0;width:100%;"
                    ):
                        # Create the whole control layout
                        self._build_mesh_control_layout()

        return layout


if __name__ == "__main__":
    import sys

    if sys.platform.startswith("linux"):
        pv.start_xvfb()
    # Add command line argument and support
    parser = argparse.ArgumentParser(description="Launch a trame server instance")
    # Add the port argument that allow user to specify the port to use for the server from command line
    parser.add_argument("--port", type=int, help="Specify the port of the server")
    # Add --server flag that is used to specify whether to use the trame as only a server and block the
    # automatic open of a browser
    parser.add_argument(
        "--server",
        action="store_true",
        help="Specify if the trame is opened as a server",
    )
    args = parser.parse_args()
    mv = TrameViewer(port=args.port)
    if sys.platform == "win32":
        # On Windows, use asyncio.run() with custom event loop policy
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(mv.run())
