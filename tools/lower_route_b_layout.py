"""Shared B-section concept geometry in world coordinates."""

from rail import RailSegment


C_PASSAGE = (0, 500, 680, 590)
GOLEM_LEDGE = (680, 495, 1340, 590)
SHIELD_LEDGE = (2160, 495, 2900, 590)
LEFT_WALL = (2800, 100, 2900, 495)
PILLBUG_LEDGE = (3060, 85, 3650, 180)
RIGHT_WALL = (3150, 355, 3290, 1100)
A_ENTRY = (4460, 90, 5000, 180)
SPIKE_TIP_Y = -200
TERRAIN = (C_PASSAGE, GOLEM_LEDGE, SHIELD_LEDGE, LEFT_WALL, PILLBUG_LEDGE, RIGHT_WALL, A_ENTRY)

# RailCarriage moves toward smaller distances on a left-facing hit.
RAIL_ONE = (
    RailSegment((3450, 280), (3698, 280)),
    RailSegment((3698, 280), (3794, 376), (3698, 376)),
    RailSegment((3794, 376), (3794, 464)),
    RailSegment((3794, 464), (3890, 560), (3890, 464)),
    RailSegment((3890, 560), (4058, 560)),
    RailSegment((4058, 560), (4154, 464), (4058, 464)),
    RailSegment((4154, 464), (4154, 376)),
    RailSegment((4154, 376), (4250, 280), (4250, 376)),
    RailSegment((4250, 280), (4620, 280)),
)
RAIL_TWO = (
    RailSegment((1160, 690), (1418, 690)),
    RailSegment((1418, 690), (1514, 594), (1418, 594)),
    RailSegment((1514, 594), (1514, 451)),
    RailSegment((1514, 451), (1610, 355), (1610, 451)),
    RailSegment((1610, 355), (1848, 355)),
    RailSegment((1848, 355), (1944, 451), (1848, 451)),
    RailSegment((1944, 451), (1944, 594)),
    RailSegment((1944, 594), (2040, 690), (2040, 594)),
    RailSegment((2040, 690), (2320, 690)),
)
