#!/usr/bin/env python

import argparse
import subprocess
import os

dirname = os.path.dirname(__file__)
streamlit_fname = os.path.join(dirname, "test_viewer_streamlit.py")


def main():
    parser = argparse.ArgumentParser(description="Streamlit-PyVista test client")
    parser.add_argument("mesh_file", nargs="+", type=str)
    args = parser.parse_args()
    files = args.mesh_file
    with open("/tmp/__toto__.tmp", "w") as f:
        f.write("\n".join(files))

    subprocess.run(
        f"streamlit run --server.headless true {streamlit_fname}", shell=True
    )


if __name__ == "__main__":
    main()
