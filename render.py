import bpy
import math
import os
import subprocess
import sys
import tempfile

_gltf_to_png_render = os.environ.get('GLTF_TO_PNG_RENDER')
if _gltf_to_png_render:
    with open(_gltf_to_png_render) as _f:
        _src = _f.read()
    _src = _src.replace("bpy.ops.render.render(write_still=True)", "pass")
    exec(compile(_src, 'gltf_to_png_render.py', 'exec'))
else:
    raise RuntimeError("GLTF_TO_PNG_RENDER not set. Run via 'nix run .'")

argv = sys.argv[sys.argv.index('--') + 1:]
num_frames = int(argv[4]) if len(argv) > 4 else 72
duration = float(argv[5]) if len(argv) > 5 else 3.0

scene = bpy.context.scene
scene.render.film_transparent = False

turntable = bpy.data.objects.new('Turntable', None)
turntable.location = center
scene.collection.objects.link(turntable)
for obj in list(bpy.data.objects):
    if obj.type == 'MESH':
        obj.parent = turntable

rot_per_frame = 360.0 / num_frames
for i in range(num_frames):
    turntable.rotation_euler = (0, 0, math.radians(rot_per_frame * i))
    turntable.keyframe_insert(data_path='rotation_euler', frame=i + 1)

scene.frame_start = 1
scene.frame_end = num_frames
fps = round(num_frames / duration)

with tempfile.TemporaryDirectory(prefix='gltf_to_webm_') as tmpdir:
    scene.render.filepath = os.path.join(tmpdir, 'frame_')
    bpy.ops.render.render(animation=True)
    subprocess.run([
        'ffmpeg', '-y',
        '-framerate', str(fps),
        '-i', os.path.join(tmpdir, 'frame_%04d.png'),
        '-c:v', 'libvpx-vp9',
        '-b:v', '2M',
        '-vf', 'format=yuv420p',
        '-an',
        output_path
    ], check=True)
