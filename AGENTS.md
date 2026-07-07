# AGENTS.md

## Run

```sh
nix run . -- -i input.gltf -o output.webm
nix run . -- -i input.gltf -o output.webm -a 90 -e 0 -n 36 -d 1.5
nix run . -- -i input.gltf -o output.webm -r report.json
```

`--` separates `nix run` args from script args. Required flags: `-i`, `-o`. Optional: `-a`/`--start-angle` (default 0), `-e`/`--elevation` (default 15 — set in the shell script), `-n`/`--num-frames` (def 72), `-d`/`--duration` sec (def 3.0), `-r`/`--report`.

## Architecture

- `render.py` — Blender Python script (`bpy` only exists inside Blender). NOT a standalone Python script. Imports scene setup from `gltf_to_png.py` (flake input) via `exec()` with the render call patched out, then adds turntable animation + ffmpeg encoding.
- `flake.nix` — Nix flake. Wraps Blender invocation, passes CLI args, provides blender + ffmpeg + gltf_to_png.py as dependencies.
- `flake.lock` — pins nixpkgs and gltf_to_png.py inputs.

## Quirks

- `bpy.ops.object.delete()` uses `confirm=` (not `confirm_confirm=`) — Blender 4.0+ API.
- ffmpeg added to PATH by the shell script (`export PATH=...`), not by `render.py`.
- Camera uses spherical positioning from gltf_to_png.py (`dx/dy/dz` with `h_rad`/`v_rad`). Turntable rotates meshes (parented to an empty), camera stays fixed.
- Report `-r` JSON uses `$DURATION` (the arg value, not hardcoded).
- EEVEE render, 512×512, PNG intermediate frames → ffmpeg VP9 WebM. Framerate = `num_frames / duration`.
- `render.py` loads `gltf_to_png.py`'s `render.py` via `exec()` after patching out its single-frame render call — the scene setup (clear, import glTF, bbox, camera, lighting) runs from the external module.

## Verification

Only check available: `nix flake check`. No tests, no CI, no linter, no typechecker.
