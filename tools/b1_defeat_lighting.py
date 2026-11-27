"""Apply colored beam spill to individual layers of the B1 defeat preview."""

from PIL import ImageChops


def apply_light(frame, light, strength=1.0):
    """Return a lit RGBA copy, using the light's alpha as the spill mask."""
    if frame.mode != "RGBA" or light.mode != "RGBA" or frame.size != light.size:
        raise ValueError("The receiver and light must be same-size RGBA images.")

    strength = max(0, min(1, strength))
    spill = light.getchannel("A")
    if strength == 0 or spill.getbbox() is None:
        return frame.copy()

    alpha = frame.getchannel("A")
    # Dark material reflects less light than lighter stone or foliage.
    reflectance = frame.convert("L").point([
        round(255 * strength * (.22 + .78 * (level / 255) ** .60))
        for level in range(256)
    ])
    coverage = ImageChops.multiply(spill, reflectance)
    visible = alpha.point([0] + [255] * 255)
    coverage = ImageChops.multiply(coverage, visible)
    color = ImageChops.multiply(light.convert("RGB"), coverage.convert("RGB"))
    result = ImageChops.screen(frame.convert("RGB"), color)
    result.putalpha(alpha)
    return result
