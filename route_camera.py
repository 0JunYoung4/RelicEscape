"""Grounded framing and a quiet jump window for the connected lower passage."""

from math import exp


ROUTE_CAMERA_ZOOM = .45
FOOT_LINE = .22
RISE_LINE = .44
FALL_LINE = .16
HORIZONTAL_RESPONSE = 10.0
VERTICAL_RESPONSE = 10.0
B_CAMERA_HEADROOM = 240


def camera_y(player_y, view_height, bottom, top):
    return max(bottom, min(top - view_height, player_y - view_height * FOOT_LINE))


class RouteCamera:
    def __init__(self):
        self.target_y = None

    def follow(self, player, camera, screen_height, bounds, dt=None):
        """Snap explicit placements; keep ordinary jumps inside a grounded frame."""
        camera.zoom = ROUTE_CAMERA_ZOOM
        view_height = screen_height / camera.zoom
        bottom, top = bounds
        previous_x = camera.x
        camera.follow(player.x)
        if dt is None or self.target_y is None:
            self.target_y = camera_y(player.y, view_height, bottom, top)
            camera.y = self.target_y
            return

        if player.grounded:
            self.target_y = camera_y(player.y, view_height, bottom, top)
        else:
            # Preserve the last landing's framing until a climb or fall leaves it.
            self.target_y = max(self.target_y, player.y - view_height * RISE_LINE)
            self.target_y = min(self.target_y, player.y - view_height * FALL_LINE)
            self.target_y = max(bottom, min(top - view_height, self.target_y))

        elapsed = max(0.0, dt)
        target_x = camera.x
        camera.x = camera._clamp_x(previous_x + (target_x - previous_x)
                                   * (1 - exp(-HORIZONTAL_RESPONSE * elapsed)))
        if abs(camera.x - target_x) < .01:
            camera.x = target_x
        y = camera.y + (self.target_y - camera.y) * (1 - exp(-VERTICAL_RESPONSE * elapsed))
        # During a long drop, keep the feet on screen even before the lag settles.
        y = min(y, player.y - view_height * .08)
        y = max(y, player.y - view_height * .72)
        camera.y = max(bottom, min(top - view_height, y))
        if abs(camera.y - self.target_y) < .01:
            camera.y = self.target_y
