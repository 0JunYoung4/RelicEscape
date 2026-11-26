"""Check the raw vertex writer against SDL's public ctypes representation."""

import unittest

from pico2d import pico2d as pico

from render_mesh import VERTEX_SIZE, pack_vertex, vertex_buffer


class RenderMeshTests(unittest.TestCase):
    def test_packed_vertices_match_sdl_constructors_byte_for_byte(self):
        samples = (
            ((0.0, -0.0), (0, 255, 127, 0), (0.0, 1.0)),
            ((-32768.125, 1440.333333333), (255, 0, 0, 255), (-.125, 1.75)),
            ((.00000012345, -98765.4321), (68, 103, 112, 47), (.333333333, .9)),
            ((2560, 540), (210, 224, 227, 123), (1, 0)),
        )
        expected = (pico.SDL_Vertex * len(samples))(
            *(pico.SDL_Vertex(position, color, uv) for position, color, uv in samples))
        actual = vertex_buffer(len(samples))
        for index, ((x, y), color, (u, v)) in enumerate(samples):
            pack_vertex(actual, index * VERTEX_SIZE, x, y, *color, u, v)
        self.assertEqual(bytes(actual), bytes(expected))

    def test_nested_geometry_build_keeps_outer_vertices_intact(self):
        outer = vertex_buffer(2)
        pack_vertex(outer, 0, 1.25, 4.5, 100, 120, 140, 160, .25, .75)
        first_vertex = bytes(outer)[:VERTEX_SIZE]
        nested = vertex_buffer(2)
        pack_vertex(nested, 0, -999, -555, 0, 0, 0, 0, 0, 0)
        pack_vertex(nested, VERTEX_SIZE, 500, 800, 255, 255, 255, 255, 1, 1)
        pack_vertex(outer, VERTEX_SIZE, 7.5, 9.25, 50, 60, 70, 80, .5, 1)
        self.assertEqual(bytes(outer)[:VERTEX_SIZE], first_vertex)
        self.assertEqual(outer[1].position.x, 7.5)
        self.assertEqual(nested[1].position.x, 500)


if __name__ == "__main__":
    unittest.main()
