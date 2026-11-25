"""Shared B-section geometry in world coordinates."""

from rail import RailSegment


C_PASSAGE = (0, 500, 680, 590)
C_APPROACH_LEDGE = (680, 495, 1340, 590)
SHIELD_LEDGE = (2160, 495, 2900, 590)
LEFT_WALL = (2800, 100, 2900, 495)
PILLBUG_LEDGE = (3060, 85, 3650, 180)
RIGHT_WALL = (3150, 355, 3290, 1100)
A_ENTRY = (4460, 90, 5000, 180)
SPIKE_TIP_Y = -200
SPIKE_BASE_Y = -244
WIDTH = A_ENTRY[2]
BACKGROUND_BOTTOM = -330
BOTTOM, TOP = -900, 1370
TERRAIN = (C_PASSAGE, C_APPROACH_LEDGE, SHIELD_LEDGE, LEFT_WALL, PILLBUG_LEDGE, RIGHT_WALL, A_ENTRY)

# The two openings in the old spike floor line up with the descending rail.
SPIKE_SHELVES = ((0, -350, 1408, SPIKE_BASE_Y), (1616, -350, 1842, SPIKE_BASE_Y),
                 (2050, -350, WIDTH, SPIKE_BASE_Y))
THORN_WALL_CROP = (106, 14, 605, 2158)
LOWER_RAIL_THORN_WALL = (1598, -250, 1860, TOP + 120)
THORN_WALLS = (
    ((3890, -265, 4130, 720), False),
    ((3940, 1020, 4080, 1620), True),
    (LOWER_RAIL_THORN_WALL, True),
)
# Horizontal extents in the trimmed sprite, in bands from the pointed end to the base.
THORN_WALL_PROFILE = (
    (117, 374), (108, 367), (36, 478), (0, 440), (19, 499), (6, 482), (8, 474), (84, 472),
    (7, 396), (90, 486), (11, 401), (76, 496), (18, 444), (62, 465), (23, 444), (87, 395),
)
# RailCarriage moves toward smaller distances on a left-facing hit.
RAIL_ONE = (
    RailSegment((3450, 280), (3698, 280)),
    RailSegment((3698, 280), (3794, 376), (3698, 376)),
    RailSegment((3794, 376), (3794, 774)),
    RailSegment((3794, 774), (3890, 870), (3890, 774)),
    RailSegment((3890, 870), (4108, 870)),
    RailSegment((4108, 870), (4204, 774), (4108, 774)),
    RailSegment((4204, 774), (4204, 376)),
    RailSegment((4204, 376), (4300, 280), (4300, 376)),
    RailSegment((4300, 280), (4620, 280)),
)
RAIL_TWO = (
    RailSegment((1160, 690), (1418, 690)),
    RailSegment((1418, 690), (1514, 594), (1418, 594)),
    RailSegment((1514, 594), (1514, -464)),
    RailSegment((1514, -464), (1610, -560), (1610, -464)),
    RailSegment((1610, -560), (1848, -560)),
    RailSegment((1848, -560), (1944, -464), (1848, -464)),
    RailSegment((1944, -464), (1944, 594)),
    RailSegment((1944, 594), (2040, 690), (2040, 594)),
    RailSegment((2040, 690), (2320, 690)),
)
