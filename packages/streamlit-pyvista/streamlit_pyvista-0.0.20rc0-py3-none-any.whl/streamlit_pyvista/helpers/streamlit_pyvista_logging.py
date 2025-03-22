import logging
import os.path

from streamlit_pyvista import DEFAULT_CACHE_DIR

DEFAULT_LOG_FILENAME = "streamlit_pyvista.logs"
STREAMLIT_PYVISTA_LOG_FORMAT = (
    "%(pathname)s:%(lineno)d:%(processName)s %(threadName)s"
    ":%(levelname)s:%(funcName)s:%(asctime)s: %(message)s"
)
logging_level = logging.INFO

# Create a root_logger
root_logger = logging.getLogger("streamlit_pyvista")
root_logger.setLevel(logging_level)

# Create handlers
console_handler = logging.StreamHandler()
os.makedirs(DEFAULT_CACHE_DIR, exist_ok=True)
file_handler = logging.FileHandler(
    os.path.join(DEFAULT_CACHE_DIR, DEFAULT_LOG_FILENAME)
)

# Set logging levels for handlers
console_handler.setLevel(logging_level)
file_handler.setLevel(logging_level)

# Create formatters
formatter = logging.Formatter(STREAMLIT_PYVISTA_LOG_FORMAT)

# Add formatters to handlers
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to root_logger
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)
