import hashlib
import json
import os

from datetime import datetime  # , timedelta
from multiprocessing import Lock
from multiprocessing.managers import SyncManager

# from typing import Optional, Callable
from typing import Optional

# import pyvista as pv
# import requests

from streamlit_pyvista import ENV_VAR_PREFIX, DEFAULT_CACHE_DIR
from streamlit_pyvista.helpers.streamlit_pyvista_logging import root_logger
from .utils import with_lock

DEFAULT_THRESHOLD = int(os.environ.get(ENV_VAR_PREFIX + "DECIMATION_THRESHOLD", 6000))
DEFAULT_TTL = int(os.environ.get(ENV_VAR_PREFIX + "CACHE_TTL_MINUTES", 60 * 24 * 90))
DEFAULT_VIEWER_CACHE_NAME = "viewer.py"


class SharedLockManager(SyncManager):
    pass


SharedLockManager.register("Lock", Lock)


def get_lock():
    manager = SharedLockManager()
    manager.start()
    return manager.Lock()


# Create a global lock
entries_lock = get_lock()
load_entries_lock = get_lock()
entry_lock = get_lock()

cached_entries = None

cache_checksum_file_path = "checksums.json"
cache_dir = DEFAULT_CACHE_DIR


@with_lock(lock=load_entries_lock)
def load_cache():

    file_path = os.path.join(cache_dir, cache_checksum_file_path)
    root_logger.debug(f"load cache from {os.path.abspath(file_path)}")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            import json

            try:
                cached_entries = json.load(f)
            except json.JSONDecodeError:
                cached_entries = {}
    else:
        cached_entries = {}
    return cached_entries


@with_lock(lock=entries_lock)
def clear_cached_entries():
    global cached_entries
    cached_entries = {}


@with_lock(lock=entries_lock)
def get_cached_entries():
    global cached_entries
    if cached_entries is not None:
        return cached_entries

    cached_entries = load_cache()
    return cached_entries


@with_lock(lock=entry_lock)
def get_cached_entry(fname):
    checksums = get_cached_entries()
    if fname in checksums:
        return checksums[fname]


@with_lock(lock=entry_lock)
def set_cached_entry(fname, entry):
    checksums = get_cached_entries()
    checksums[fname] = entry
    root_logger.debug(f"set cache entry {checksums[fname]}")


@with_lock(lock=entries_lock)
def save_cached_entries():
    file_path = os.path.join(cache_dir, cache_checksum_file_path)
    import copy

    global cached_entries
    c = copy.deepcopy(cached_entries)
    if c is None:
        c = {}

    cached_entries = load_cache()
    cached_entries.update(c)
    root_logger.debug(
        f"saving cache {cached_entries.keys()} to {os.path.abspath(file_path)}"
    )
    with open(file_path, "w") as f:
        import json

        json.dump(cached_entries, f, indent=4)
        f.flush()


def save_file_content(
    cache_id: str, uri=None, content=None, cache_dir=DEFAULT_CACHE_DIR, sync=True
) -> dict:
    """
    Save file content to a cache, optionally process it, and return the path.

    Args:
        file_content(bytes): Content of the file to save in the cache
        save_path(str): {Cache directory}/{filename} to ideally store the content. The checksum will be added to
        the filename
        ttl_minutes(int): Time to live of the element in the cache
        process_func(Optional[Callable]): Optional function to process the file (e.g., decimation for meshes)
        process_args(Optional[dict]): Optional arguments for the process_func

    Returns:
        tuple[str, Optional[str]]: A tuple with The path to the saved file and its processed version if there exists one

    Note:
        The cache works as follows:
            - The hash of content passed as argument is computed. If one entry with the same hash exists already in the\
            cache json, we take the file that was stored in it (we try to take the processed one if it exists) and we\
            update the last access time to avoid deleting it if it was recently used
            - If the hash is not in the cache then a new entry is created and the content is processed with the\
            function passed as parameter if there is one
            - Then the function return the path to the processed file in priority and to the original file if no\
            processing happened
    """
    # Compute checksum and create the cache directory
    if uri is None:
        uri = cache_id
    cache_entry = get_cached_entry(cache_id)
    root_logger.debug(f"id={cache_id} cache_entry={cache_entry} cache_dir={cache_dir}")

    # Check if file exists in cache
    if cache_entry is not None:
        root_logger.debug(f"Found a cached entry: {cache_entry}")
    else:
        root_logger.warning(f"No matching file already stored to {cache_id}")
        os.makedirs(cache_dir, exist_ok=True)
        # read content
        try:
            content = content.read()
        except Exception:
            pass

        # compute checksum
        computed_checksum = hashlib.sha256(content).hexdigest()
        # do not copy an existing file path
        if not os.path.exists(uri):
            # forge filename
            name, extension = os.path.splitext(cache_id)
            name = os.path.split(name)[1]
            filename_with_checksum = f"{name}_{computed_checksum}{extension}"

            # write cache file
            cache_file_path = os.path.join(cache_dir, filename_with_checksum)
            root_logger.info(
                f"create cache file {cache_file_path} {filename_with_checksum} {cache_dir}"
            )

            with open(cache_file_path, "wb") as f:
                f.write(content)
        else:
            cache_file_path = uri

        # Create new entry in cache
        set_cached_entry(
            cache_id,
            {
                "filename": cache_file_path,
                "uri": uri,
                "checksum": computed_checksum,
                "creation": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
        )
        root_logger.debug(f"Created new cache entry: {get_cached_entry(cache_id)}")
        if sync:
            save_cached_entries()

    res = get_cached_entry(cache_id)
    root_logger.debug(f"get_cached_entry({cache_id}) = {res}")
    return res


def save_mesh_content(
    mesh_content: bytes,
    save_dir: str,
    ttl_minutes: int = DEFAULT_TTL,
    decimation_factor: float = None,
    decimation_threshold: int = DEFAULT_THRESHOLD,
) -> tuple[str, Optional[str]]:
    """
    Save mesh content to a cache, optionally decimate it, and return the path.

    Args:
        mesh_content(bytes): content of the mesh
        save_dir(str): {Cache directory}/{filename} to ideally store the content. The checksum will be added to the
        filename.
        ttl_minutes(int): Time to live of the element in the cache
        decimation_factor(float): The reduction factor to aim. e.g. decimation_factor = 0.25, initial mesh number of
        cells 1000
            -> resulting mesh will have 750 cells
        decimation_threshold(int): The threshold under which we don't decimate the mesh

    Returns
        str: The path to file decimated or not (depending on the threshold) in the cache
    """
    # process_args = {
    #     "decimation_factor": decimation_factor,
    #     "decimation_threshold": decimation_threshold,
    # }
    # return save_file_content(
    #     mesh_content, save_dir, ttl_minutes, process_mesh, process_args
    # )
    return save_file_content(mesh_content, save_dir, ttl_minutes)


def update_cache(cache_directory: str = DEFAULT_CACHE_DIR):
    """
    Update the cache by removing entries that are out of ttl

    Args:
        cache_directory(str): The directory in which the cache is stored
    """
    # Open the cache file
    checksum_file = os.path.join(cache_directory, "checksums.json")
    if not os.path.exists(checksum_file):
        return

    with open(checksum_file, "r") as f:
        try:
            checksums = json.load(f)
        except json.JSONDecodeError:
            return

    # Check if the entries are still valid
    # current_time = datetime.now()
    keys_to_remove = []
    for filename, entry in checksums.items():
        pass
        # creation_date = datetime.strptime(entry["creation"], "%Y-%m-%d %H:%M:%S")
        # if current_time - creation_date > timedelta(minutes=DEFAULT_TTL):
        #    keys_to_remove.append((filename, entry.get("processed_path", None)))

    root_logger.info(
        f"Update cache: found {len(keys_to_remove)} invalid entries. Trying to remove "
        f"{', '.join(list(map(lambda x: x[0], keys_to_remove)))}"
    )
    # Remove the keys of old entries
    for key in keys_to_remove:
        if os.path.exists(os.path.join(cache_directory, key[0])):
            os.remove(os.path.join(cache_directory, key[0]))
        if key[1] is not None and os.path.exists(os.path.join(cache_directory, key[1])):
            os.remove(os.path.join(cache_directory, key[1]))
        root_logger.debug(f"Cache - Removed {key[0]} from cache")
        del checksums[key[0]]

    # Rewrite the checksums.json file
    with open(checksum_file, "w") as f:
        json.dump(checksums, f, indent=4)
