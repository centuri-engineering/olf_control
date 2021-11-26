"""Forked from the openflexure microscope server code here:
²
https://gitlab.com/openflexure/openflexure-microscope-server/-/blob/master/openflexure_microscope/utilities.py


"""
import base64
import copy
import logging
import sys
import time
from contextlib import contextmanager
from typing import Dict, List, Optional, Sequence, Tuple, Type, Union

import numpy as np

# TypedDict was added to typing in 3.8. Use typing_extensions for <3.8
if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict


JSONArrayType = TypedDict(
    "JSONArrayType",
    {"@type": str, "base64": str, "dtype": str, "shape": Tuple[int, ...]},
)


def deserialise_array_b64(
    b64_string: str, dtype: Union[Type[np.dtype], str], shape: Tuple[int, ...]
):
    flat_arr: np.ndarray = np.frombuffer(base64.b64decode(b64_string), dtype)
    return flat_arr.reshape(shape)


def serialise_array_b64(npy_arr: np.ndarray) -> Tuple[str, str, Tuple[int, ...]]:
    b64_string: str = base64.b64encode(npy_arr.tobytes()).decode("ascii")
    dtype: str = str(npy_arr.dtype)
    shape: Tuple[int, ...] = npy_arr.shape
    return b64_string, dtype, shape


def ndarray_to_json(arr: np.ndarray) -> JSONArrayType:
    if isinstance(arr, memoryview):
        # We can transparently convert memoryview objects to arrays
        # This comes in very handy for the lens shading table.
        arr = np.array(arr)
    b64_string, dtype, shape = serialise_array_b64(arr)
    return {"@type": "ndarray", "dtype": dtype, "shape": shape, "base64": b64_string}


def json_to_ndarray(json_dict: JSONArrayType):
    if json_dict.get("@type") != "ndarray":
        logging.warning("No valid @type attribute found. Conversion may fail.")
    for required_param in ("dtype", "shape", "base64"):
        if not json_dict.get(required_param):
            raise KeyError(f"Missing required key {required_param}")

    b64_string: Optional[str] = json_dict.get("base64")
    dtype: Optional[str] = json_dict.get("dtype")
    shape: Optional[Tuple[int, ...]] = json_dict.get("shape")

    if b64_string and dtype and shape:
        return deserialise_array_b64(b64_string, dtype, shape)
    else:
        raise ValueError("Required parameters for decoding are missing")
