"""Shared horizontal hit displacement for grounded enemies."""

from slash_effect import FORWARD_SLASH_REACH


KNOCKBACK_DURATION = .20
KNOCKBACK_SPEED = 2 * FORWARD_SLASH_REACH / KNOCKBACK_DURATION


def advance_knockback(dt, remaining, facing, body, terrain, world_width, support_edges):
    """Return this frame's signed push and the remaining time, clipped to solid ground."""
    step = min(dt, remaining)
    if step <= 0:
        return 0.0, remaining

    requested = KNOCKBACK_SPEED * step * (remaining - step / 2) / KNOCKBACK_DURATION
    distance = requested
    x, bottom, width, height = body
    left, right = x - width / 2, x + width / 2
    support_left, support_right = support_edges or (0, world_width)
    if facing > 0:
        distance = min(distance, max(0.0, min(world_width, support_right) - right))
    else:
        distance = min(distance, max(0.0, left - max(0, support_left)))
    for x1, y1, x2, y2 in terrain:
        if bottom >= y2 or bottom + height <= y1:
            continue
        if facing > 0 and right <= x1:
            distance = min(distance, x1 - right)
        elif facing < 0 and left >= x2:
            distance = min(distance, left - x2)
    return facing * distance, remaining - step if distance == requested else 0.0
