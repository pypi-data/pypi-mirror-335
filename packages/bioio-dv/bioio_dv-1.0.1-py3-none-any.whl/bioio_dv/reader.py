#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import xarray as xr
from bioio_base import constants, dimensions, exceptions, io, reader, types
from fsspec.implementations.local import LocalFileSystem
from fsspec.spec import AbstractFileSystem
from mrc import DVFile
from resource_backed_dask_array import resource_backed_dask_array

###############################################################################


class Reader(reader.Reader):
    """
    The main class of each reader plugin. This class is subclass
    of the abstract class reader (BaseReader) in bioio-base.

    Parameters
    ----------
    image: Any
        Some type of object to read and follow the Reader specification.
    fs_kwargs: Dict[str, Any]
        Any specific keyword arguments to pass down to the fsspec created filesystem.
        Default: {}

    Notes
    -----
    It is up to the implementer of the Reader to decide which types they would like to
    accept (certain readers may not support buffers for example).

    """

    _xarray_dask_data: Optional["xr.DataArray"] = None
    _xarray_data: Optional["xr.DataArray"] = None
    _mosaic_xarray_dask_data: Optional["xr.DataArray"] = None
    _mosaic_xarray_data: Optional["xr.DataArray"] = None
    _dims: Optional[dimensions.Dimensions] = None
    _metadata: Optional[Any] = None
    _scenes: Optional[Tuple[str, ...]] = None
    _current_scene_index: int = 0
    # Do not provide default value because
    # they may not need to be used by your reader (i.e. input param is an array)
    _fs: "AbstractFileSystem"
    _path: str

    @staticmethod
    def _is_supported_image(fs: AbstractFileSystem, path: str, **kwargs: Any) -> bool:
        return DVFile.is_supported_file(path)

    def __init__(self, image: types.PathLike, fs_kwargs: Dict[str, Any] = {}):
        self._fs, self._path = io.pathlike_to_fs(
            image,
            enforce_exists=True,
            fs_kwargs=fs_kwargs,
        )
        # Catch non-local file system
        if not isinstance(self._fs, LocalFileSystem):
            raise NotImplementedError(
                f"dv reader not yet implemented for non-local file system. "
                f"Received URI: {self._path}, which points to {type(self._fs)}."
            )

        if not self._is_supported_image(self._fs, self._path):
            raise exceptions.UnsupportedFileFormatError(
                self.__class__.__name__, self._path
            )

    @property
    def scenes(self) -> Tuple[str, ...]:
        return ("Image:0",)

    def _read_delayed(self) -> xr.DataArray:
        return self._xarr_reformat(delayed=True)

    def _read_immediate(self) -> xr.DataArray:
        return self._xarr_reformat(delayed=False)

    def _xarr_reformat(self, delayed: bool) -> xr.DataArray:
        with DVFile(self._path) as dv:
            xarr = dv.to_xarray(delayed=delayed, squeeze=False)
            if delayed:
                xarr.data = resource_backed_dask_array(xarr.data, dv)
            xarr.attrs[constants.METADATA_UNPROCESSED] = xarr.attrs.pop("metadata")
        return xarr

    @property
    def physical_pixel_sizes(self) -> types.PhysicalPixelSizes:
        """
        Returns
        -------
        sizes: PhysicalPixelSizes
            Using available metadata, the floats representing physical pixel sizes for
            dimensions Z, Y, and X.

        Notes
        -----
        We currently do not handle unit attachment to these values. Please see the file
        metadata for unit information.
        """
        with DVFile(self._path) as dvfile:
            return types.PhysicalPixelSizes(*dvfile.voxel_size[::-1])
