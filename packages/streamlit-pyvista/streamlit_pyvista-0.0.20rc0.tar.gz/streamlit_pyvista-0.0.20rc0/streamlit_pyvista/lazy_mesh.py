from typing import Optional

import pyvista as pv
import os
from pyvista import DataSet
import validators
import requests
import streamlit_pyvista.helpers.cache as cache
from streamlit_pyvista.helpers.utils import is_web_link

from streamlit_pyvista import ENV_VAR_PREFIX
from streamlit_pyvista.helpers.streamlit_pyvista_logging import root_logger

DEFAULT_THRESHOLD = int(os.environ.get(ENV_VAR_PREFIX + "DECIMATION_THRESHOLD", 6000))


class LazyMesh:
    """
    LazyMesh is a class that is a pyvista mesh container that loads the mesh only when its first requested
    """

    def __init__(self, path, cache_dir=None):
        if not isinstance(path, str):
            raise RuntimeError(f"path must be a string not {type(path)}")
        self.path = path
        self._is_available = False
        self._full_mesh = None
        self._decimated_mesh = None
        self._expect_decimated = True
        self.cache_dir = cache_dir

    def get_checksum(self):
        checksums = self.get_cached_checksums()
        return checksums[self.path]

    def load(self) -> pv.DataSet:
        """
        This function load the mesh after having inserted it in the cache

        Returns:
            pv.DataSet: the decimated mesh if it exists else the original mesh
        """
        root_logger.debug(f"self.path = {self.path}")
        if is_web_link(self.path):
            full_mesh_path, decimated_mesh_path = self._save_mesh_content_from_url()
        else:
            cache_entry = self._save_mesh_content_from_file()
            full_mesh_path = cache_entry["filename"]
        self._full_mesh = pv.read(full_mesh_path)
        self._is_available = True
        root_logger.debug("decimate is off: needs to rewrite")
        # if decimated_mesh_path:
        #    self._decimated_mesh = pv.read(decimated_mesh_path)
        #    return self._decimated_mesh
        return full_mesh_path

    def _save_mesh_content_from_url(
        self,
        decimation_factor: float = None,
        decimation_threshold: int = DEFAULT_THRESHOLD,
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Save mesh content from a URL to a cache, optionally decimate it, and return the path.

        Args:
            ttl_minutes(int): Time to live of the element in the cache
            decimation_factor(float): The reduction factor to aim. e.g. decimation_factor = 0.25, initial mesh number of
            cells 1000 -> resulting mesh will have 750 cells
            decimation_threshold(int): The threshold under which we don't decimate the mesh
        Returns
            Optional[str]: The path to file decimated or not (depending on the threshold) in the cache
        """
        url = self.path
        response = requests.get(url)
        if response.status_code != 200:
            return None, None
        root_logger.debug(f"Cache - Saving {url} in the cache...")
        # process_args = {
        #     "decimation_factor": decimation_factor,
        #     "decimation_threshold": decimation_threshold,
        # }
        raise RuntimeError("broken")
        # return cache.save_file_content(
        #     response.content, self.target_path, process_mesh, process_args
        # )

    def _save_mesh_content_from_file(
        self,
        decimation_factor: float = None,
        decimation_threshold: int = DEFAULT_THRESHOLD,
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Save mesh content from a file to a cache, optionally decimate it, and return the path.

        Args:
            the filename
            decimation_factor(float): The reduction factor to aim. e.g. decimation_factor = 0.25, initial mesh number of
            cells 1000 -> resulting mesh will have 750 cells
            decimation_threshold(int): The threshold under which we don't decimate the mesh
        Returns
            Optional[str]: The path to file decimated or not (depending on the threshold) in the cache
        """
        if not os.path.exists(self.path):
            return None, None

        checksum = cache.get_cached_entry(self.path)
        root_logger.debug(f"{self.path} {checksum}")
        cache_entry = None
        with open(self.path, "rb") as f:
            cache_entry = cache.save_file_content(
                cache_id=self.path, content=f, cache_dir=self.cache_dir, sync=False
            )

        # process_args = {
        #     "decimation_factor": decimation_factor,
        #     "decimation_threshold": decimation_threshold,
        # }
        # result_path = cache.save_file_content(
        #     self.path, content, process_mesh, process_args
        # )
        root_logger.debug(f"new entry {cache_entry}")
        return cache_entry

    def set_decimated_as_default(self, v):
        """
        Set the default version of the mesh that is return by the mesh property
        """
        self._expect_decimated = v

    @property
    def is_available(self) -> bool:
        """
        Define whether the mesh was already loaded

        Returns:
            bool: True if the mesh is available, False otherwise
        """
        return self._is_available

    def has_decimated(self) -> bool:
        """
        Get if the mesh has a decimated version of it

        Returns:
            bool: True if the mesh has a decimated version of it, and False if it doesn't or if it still wasn't loaded
        """
        if self._is_available and self._decimated_mesh:
            return True
        return False

    def decimated_mesh(self) -> pv.DataSet:
        """
        Try to get the decimated version of the mesh

        Returns:
            pv.DataSet: The decimated version of the mesh, and if it doesn't exist, return the original version
            of the mesh
        """

        if self._decimated_mesh:
            return self._decimated_mesh

        if self._full_mesh:
            return self._full_mesh

        return self._load_mesh()

    @property
    def full_mesh(self) -> pv.DataSet:
        """
        Get the original version of the mesh

        Returns:
            pv.DataSet: The original(without any decimation applied) version of the mesh
        """
        if self._full_mesh:
            return self._full_mesh

        return self._load_mesh()

    @property
    def mesh(self) -> pv.DataSet:
        """
        Get the mesh requested by the user. It automatically chose the best one depending if the decimated mesh exists
        and if the user asked for the decimated on with the set_decimated_as_default function

        Returns:
            pv.DataSet: Get the mesh preferred by the user if possible. If not, just returns the original mesh
        """
        if self._decimated_mesh and self._expect_decimated:
            return self._decimated_mesh

        if self._full_mesh:
            return self._full_mesh

        return self.load()

    def get_decimated_content(pv_mesh_instance: DataSet, file_ext: str) -> str:
        """
        This function extract the String that represent a mesh.

        Args:
            pv_mesh_instance (DataSet): The mesh from which you want to get the String representation.
            file_ext (str): The file extension of the mesh.

        Returns:
            str: A string representing the mesh.

        Note:
            It could be then be written in a file and read by pv.read function.
            This function is mainly copied from pv.DataDet.save method.
        """
        if pv_mesh_instance._WRITERS is None:
            raise NotImplementedError(
                f"{pv_mesh_instance.__class__.__name__} writers are not specified,"
                " this should be a dict of (file extension: vtkWriter type)"
            )

        if file_ext not in pv_mesh_instance._WRITERS:
            raise ValueError(
                "Invalid file extension for this data type."
                f" Must be one of: {pv_mesh_instance._WRITERS.keys()}"
            )

        # store complex and bitarray types as field data
        pv_mesh_instance._store_metadata()

        writer = pv_mesh_instance._WRITERS[file_ext]()
        writer.SetInputData(pv_mesh_instance)
        writer.SetWriteToOutputString(1)
        writer.Write()
        return writer.GetOutputString()


class LazyMeshList(list[Optional[LazyMesh]]):
    """
    LazyMeshList class is child of the list class designed to contain None or LazyMesh, and to support certain features
    of the LazyMesh such as setting default version of mesh requested for the whole list or checking if a specific item
    possess a decimated version of the mesh
    """

    def __init__(self, cache_dir):
        super().__init__()
        self._expect_decimated = True
        self.loaded_count = 0
        self.cache_dir = cache_dir
        self.missing_meshes = set()

    def append(self, path):
        if isinstance(path, LazyMesh):
            super().append(path)
            return

        elif is_web_link(path):
            if not validators.url(path):
                root_logger.error(f"The link {path} is not valid")
                self.mesh_array.append(None)
                return

        elif not os.path.exists(path):
            # If the file does not exist mark it as missing to notify it in the response
            self.missing_meshes.add(path)
            return

        super().append(LazyMesh(path, cache_dir=self.cache_dir))

    def set_show_decimated(self, v):
        """
        Set behaviour of the list, if true then all item retrieve will be decimated mesh, else the list
        will return original version of the mesh
        """
        self._expect_decimated = v

    def load_meshes(self):
        for m in self:
            m.load()

    def load_mesh(self, index: int):
        m: Optional[LazyMesh] = super().__getitem__(index)
        if m is not None:
            m.load()
            return m
        return None

    def sync_cache(self):
        cache.save_cached_entries()

    def __getitem__(self, item: int) -> Optional[pv.DataSet]:
        """
        Get the mesh at a specific index

        Args:
            item (int): Index accessed

        Returns:
            Optional[pv.DataSet]: The mesh (decimated or not depending on what was defined with set_show_decimated)
            at the index specified
        """
        m: LazyMesh = super().__getitem__(item)
        if m is None:
            return m
        m.set_decimated_as_default(self._expect_decimated)
        if not m.is_available:
            self.loaded_count += 1

        return m.mesh

    def has_decimated_version(self, idx: int) -> bool:
        """
        Get whether the mesh at an index has a decimated version of itself

        Returns:
            bool: True if the mesh has a decimated version, False if it doesn't of if the mesh is None
        """
        m = super().__getitem__(idx)
        if m is None:
            return False
        return m.has_decimated()

    def number_mesh_loaded(self) -> int:
        """
        Get the number of loaded meshes in the list

        Returns:
            int: The count of loaded meshes
        """
        return self.loaded_count

    def __len__(self) -> int:
        return super().__len__()


################################################################
def compute_decimation_factor(
    current_nbr_points: float, target_nbr_points: float
) -> float:
    """
    Compute the decimation reduction factor required to get to a target size number of points.

    Args:
        current_nbr_points(float): The number of points of the initial mesh.
        target_nbr_points(float): The number of points aimed after decimation.

    Returns:
        float: The decimation_factor required to reach the target
    """
    return min(1 - target_nbr_points / current_nbr_points, 1.0)


def process_mesh(
    file_path: str, save_dir: str, decimation_factor: float, decimation_threshold: int
) -> Optional[str]:
    """
    Decimate a mesh and store it in a file

    Args:
        file_path(str): The path to the mesh to decimate
        save_dir(str): The directory in which we should save the decimated mesh
        decimation_factor(float): The reduction factor to aim. e.g. decimation_factor = 0.25, initial mesh number of
        cells 1000 -> resulting mesh will have 750 cells
        decimation_threshold(int): The threshold under which we don't decimate the mesh
    Returns:
        Optional[str]: the path to the decimated mesh or None if the mesh is under the decimation threshold
    """
    m = pv.read(file_path)
    nbr_points = m.GetNumberOfCells()
    # If the number of points is already below the threshold, we don't decimate
    if nbr_points < decimation_threshold:
        return None
    if not decimation_factor:
        decimation_factor = compute_decimation_factor(nbr_points, DEFAULT_THRESHOLD)
    root_logger.debug(
        f"Cache - Processing mesh with {nbr_points} points and using a decimation factor of {decimation_factor}"
    )
    return decimated_mesh_from_file(m, save_dir, decimation_factor)


def decimated_mesh_from_file(
    mesh: pv.DataSet, save_dir: str, decimation_factor: float = 0.5
) -> str:
    """
    Decimate a mesh and store it in a file.

    Args:
        mesh (pv.DataSet): The mesh you want to decimate.
        save_dir (str): The directory in which to save the decimated mesh.
        decimation_factor (float, optional): The reduction factor to aim for. Defaults to 0.5.
            E.g., if decimation_factor = 0.25 and the initial mesh has 1000 cells,
            the resulting mesh will have 750 cells.

    Returns:
        str: The path to the decimated mesh.

    Note:
        For more information about decimation using PyVista, see:
        https://docs.pyvista.org/version/stable/examples/01-filter/decimate#decimate-example
    """

    raise RuntimeError("broken")
    # pv_mesh = (
    #     mesh.triangulate()
    #     .extract_geometry()
    #     .decimate(decimation_factor, attribute_error=True)
    #     .sample(mesh)
    # )
    #
    # content = get_decimated_content(pv_mesh, ".vtk")
    # checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
    # save_path = f"{save_dir}/{checksum}.vtk"
    # if not os.path.exists(save_path):
    #     pv_mesh.save(save_path)
    # return save_path
