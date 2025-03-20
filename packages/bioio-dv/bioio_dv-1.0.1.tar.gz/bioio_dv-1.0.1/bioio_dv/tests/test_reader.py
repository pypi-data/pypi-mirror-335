#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Tuple

import numpy as np
import pytest
from bioio_base import dimensions, exceptions, test_utilities

from bioio_dv import Reader

from .conftest import LOCAL_RESOURCES_DIR


@pytest.mark.parametrize(
    "filename, "
    "set_scene, "
    "expected_scenes, "
    "expected_shape, "
    "expected_dtype, "
    "expected_dims_order, "
    "expected_channel_names, "
    "expected_physical_pixel_sizes",
    [
        pytest.param(
            "example.txt",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            marks=pytest.mark.xfail(raises=exceptions.UnsupportedFileFormatError),
        ),
        (
            "DV_siRNAi-HeLa_IN_02.r3d_D3D.dv",
            "Image:0",
            ("Image:0",),
            (4, 1, 40, 512, 512),
            np.int16,
            "CTZYX",
            ["360/457", "490/528", "555/617", "640/685"],
            (0.20000000298023224, 0.06502940505743027, 0.06502940505743027),
        ),
        (
            "DV_siRNAi-HeLa_IN_02.r3d",
            "Image:0",
            ("Image:0",),
            (1, 4, 40, 512, 512),
            np.dtype(">i2"),
            dimensions.DEFAULT_DIMENSION_ORDER,
            ["0/0", "0/0", "0/0", "0/0"],
            (0.20000000298023224, 0.06502940505743027, 0.06502940505743027),
        ),
    ],
)
def test_dv_reader(
    filename: str,
    set_scene: str,
    expected_scenes: Tuple[str, ...],
    expected_shape: Tuple[int, ...],
    expected_dtype: np.dtype,
    expected_dims_order: str,
    expected_channel_names: List[str],
    expected_physical_pixel_sizes: Tuple[float, float, float],
) -> None:
    # Construct full filepath
    uri = LOCAL_RESOURCES_DIR / filename

    # Run checks
    test_utilities.run_image_file_checks(
        ImageContainer=Reader,
        image=uri,
        set_scene=set_scene,
        expected_scenes=expected_scenes,
        expected_current_scene=set_scene,
        expected_shape=expected_shape,
        expected_dtype=expected_dtype,
        expected_dims_order=expected_dims_order,
        expected_channel_names=expected_channel_names,
        expected_physical_pixel_sizes=expected_physical_pixel_sizes,
        expected_metadata_type=dict,
    )
