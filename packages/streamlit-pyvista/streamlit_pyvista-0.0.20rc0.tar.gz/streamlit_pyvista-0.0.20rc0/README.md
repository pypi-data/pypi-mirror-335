# Streamlit PyVista
[![PyPI version](https://badge.fury.io/py/streamlit-pyvista.svg)](https://badge.fury.io/py/streamlit-pyvista)
[![Read the Docs](https://readthedocs.org/projects/streamlit_pyvista/badge/?version=latest)](http://streamlit-pyvista.readthedocs.io/)

A Streamlit component that allow support for new pyvista viewer backend : Trame. 

# Installation instructions
````sh
pip install streamlit-pyvista
````
# Usage Instructions

````python
import streamlit as st
from streamlit_pyvista.mesh_viewer_component import MeshViewerComponent


def main():
    st.title("Simple Streamlit App With Pyvista Viewer")

    mesh_viewer = MeshViewerComponent(
        "https://gitlab.com/dcsm/streamlit-pyvista/-/raw/main/examples/assets/plate_hole.vtu")
    mesh_viewer2 = MeshViewerComponent("assets/plate_hole.vtu")

    mesh_viewer.show()
    mesh_viewer2.show()


if __name__ == "__main__":
    main()
````
Note that instead of a file path or a url it's also possible to pass an array of link or path to display a sequence
of files.

This viewer leverage the capabilities of the new pyvista backend `Trame`, beyond  the nice design revamp, 
it also supports remote rendering.

# Package documentation
You can find the automatic documentation generated with sphinx [here](https://streamlit-pyvista.readthedocs.io/)

# Workflow overview

This package has 3 different components: 
- The Streamlit component
- The Trame viewers
- A "Server manager"

## Streamlit component
This pyvista new backend requires now to have its own server for each instance of a pyvista plotter. This means that the
streamlit component can be as simple as an iframe and displayed in the app and can use a simple api to communicate with 
the trame server and the server manger

## Trame viewers
The Trame viewers are the servers that are embeded in the streamlit app, it has exposed api endpoints that allow the 
component to communicate with the server for action such as loading a mesh in the viewer.

## Server manager
As said earlier, the trame viewers can only display one plotter at a time which means that if we want to display 
multiple plotters we need multiple servers. The job of the Server manager is to control how many trame viewers exists, 
if they need to killed or if they can be reused for other viewers

## Workflow
These 3 components interact the following manner:
1) A `MeshViewerComponent` is created and notify a `ServerManager` that it needs a viewer.
2) The `ServerManager` look if he have idling trame viewer anf if not, it start a new server.
3) The `ServerManager` specify the endpoints of the server that can be used to the `MeshViewerComponent`
4) The `MeshViewerComponent` directly communicate with the api of the trame viewer via the endpoints 
specified by the `ServerManager` 

