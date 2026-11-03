---
name: pixelfx
description: Create and export code-rendered pixel-art effects for games using patch-gg/pixelfx. Use for slash trails, impacts, particles, pickup effects, and transparent VFX sprite sheets.
---

# pixelfx

Use a separate checkout of [patch-gg/pixelfx](https://github.com/patch-gg/pixelfx) with Node.js 18 or newer. Reuse an existing checkout when available. Otherwise clone into a writable tools or temporary directory when network access permits. Run the commands below from that checkout. The renderer runs directly with Node. FFmpeg is optional for GIF and MP4 previews.

1. Search for a close match with `node tools/list.mjs slash` (replace `slash` with the effect keyword). Use `docs/CATALOG.md` to browse by category.
2. Run `node tools/render.mjs fire/torch` as a smoke test or substitute the selected effect ID. Inspect `records/<id>/contact.png` with an image viewer. Adjust palette, direction, and effect-specific options with `--opts`. Check readability at the intended game scale and review the animation timing before export.
3. For a new effect, read `docs/AUTHORING.md`, start from a close example or `node tools/new.mjs <id>`, and iterate on rendered frames. Run `node tools/check.mjs <id>` after changing effect code.
4. Export with `node tools/render.mjs <id> --sheet`. Keep the transparent PNG and companion JSON together. Use the JSON's frame timing and pivot when integrating. Copy only the requested assets into the game project and preserve the applicable upstream license and notices when distributing upstream material.

## RelicEscape

Follow the project's AGENTS.md. Base player poses on `assets/concepts/player-sd-idle-right-source-v3.png`. Export effects separately from the player artwork. For attacks, use upstream act timing as a reference for wind-up, release, hit-stop, and recovery, then align the effect with the game's attack animation. Choose frame size based on the production asset and its in-game scale.

If the renderer is unavailable, report which dependency or access check failed and distinguish a proposed effect from a verified export.
