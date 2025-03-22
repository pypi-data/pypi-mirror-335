#!/usr/bin/env python

import streamlit as st
from streamlit_pyvista.mesh_viewer_component import MeshViewerComponent
from streamlit_pyvista.server_managers import ServerManagerProxified  # noqa: E402
from streamlit_pyvista.trame_viewers import get_advanced_viewer_path  # noqa: E402


def main():
    st.title("Simple Streamlit App With Pyvista Viewer")

    files = open("/tmp/__toto__.tmp").read().split()
    print(f"loading {len(files)} files")
    mesh_viewer = MeshViewerComponent(
        files,
        trame_viewer_class=get_advanced_viewer_path(),
        server_manager_class=ServerManagerProxified,
    )
    st.warning("Creation viewer done")
    mesh_viewer.show()


if __name__ == "__main__":
    main()
