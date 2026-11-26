"""Build SDL geometry without allocating an object for each vertex."""

from ctypes import c_int, sizeof
from functools import lru_cache
from math import cos, sin, tau
from struct import Struct

from pico2d import pico2d as pico


_VERTEX = Struct("=ffBBBBff")
VERTEX_SIZE = _VERTEX.size
if (sizeof(pico.SDL_Vertex) != VERTEX_SIZE
        or tuple(getattr(pico.SDL_Vertex, name).offset
                 for name in ("position", "color", "tex_coord")) != (0, 8, 12)):
    raise RuntimeError("Unsupported SDL_Vertex memory layout")

# The SDL array exposes a writable buffer. Packing writes the same float32/RGBA
# bytes as SDL_Vertex's constructors, without their point/color conversions.
pack_vertex = _VERTEX.pack_into


def vertex_buffer(count):
    """Return a fresh array so nested geometry submissions cannot overwrite it."""
    return (pico.SDL_Vertex * count)()


@lru_cache(maxsize=128)
def index_buffer(indices):
    """Cache a tuple's SDL indices. Callers must treat the result as read-only."""
    return (c_int * len(indices))(*indices)


@lru_cache(maxsize=128)
def grid_indices(columns, rows):
    """Return read-only indices for a grid of cells in the existing SDL winding."""
    stride = columns + 1
    indices = []
    for row in range(1, rows + 1):
        for column in range(1, stride):
            corner = row * stride + column
            indices.extend((corner - stride - 1, corner - stride, corner - 1,
                            corner - stride, corner, corner - 1))
    return (c_int * len(indices))(*indices)


@lru_cache(maxsize=16)
def unit_circle(steps):
    """Keep the original angle order and float calculations for light rings."""
    return tuple((cos(tau * index / steps), sin(tau * index / steps))
                 for index in range(steps))
