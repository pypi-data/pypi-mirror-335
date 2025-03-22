import os

ENV_VAR_PREFIX = "STREAMLIT_PYVISTA_"
ROOT_URL = os.environ.get(ENV_VAR_PREFIX+"BASE_URL_PATH", "")
REMOTE_HOST = os.environ.get(ENV_VAR_PREFIX+"REMOTE_HOST", "http://127.0.0.1")
DEFAULT_CACHE_DIR = os.environ.get(ENV_VAR_PREFIX + "CACHE_DIR_NAME", ".streamlit-pyvista-cache")
