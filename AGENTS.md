# AGENTS.md

## Run

```sh
nix run . -- -i input.gltf -o output.webm
nix run . -- -i input.gltf -o output.webm -a 90 -e 0 -n 36 -d 1.5
nix run . -- -i input.gltf -o output.webm -r report.json
```

`--` separates `nix run` args from script args. Required flags: `-i`, `-o`. Optional: `-a`/`--start-angle` (default 0), `-e`/`--elevation` (default 15 — set in `render.py` line 13, not the shell script), `-n`/`--num-frames` (def 72), `-d`/`--duration` sec (def 3.0), `-r`/`--report`.

## Architecture

- `render.py` — Blender Python script (`bpy` only exists inside Blender). NOT a standalone Python script.
- `flake.nix` — Nix flake. Wraps Blender invocation, passes CLI args, provides blender + ffmpeg as dependencies. No other build system, no `pyproject.toml`, no `requirements.txt`.
- `flake.lock` — pin nixpkgs input.

## Quirks

- `bpy.ops.object.delete()` uses `confirm=` (not `confirm_confirm=`) — Blender 4.0+ API.
- ffmpeg added to PATH by the shell script (`export PATH=...`), not by `render.py`.
- Camera uses spherical positioning from gltf_to_png.py (`dx/dy/dz` with `h_rad`/`v_rad`). Turntable rotates meshes (parented to an empty), camera stays fixed.
- Report `-r` JSON uses `$DURATION` (the arg value, not hardcoded).
- EEVEE render, 512×512, PNG intermediate frames → ffmpeg VP9 WebM. Framerate = `num_frames / duration`.

## Verification

Only check available: `nix flake check`. No tests, no CI, no linter, no typechecker.
