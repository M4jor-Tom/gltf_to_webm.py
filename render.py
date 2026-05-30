import bpy
import math
import mathutils
import os
import subprocess
import sys
import tempfile

argv = sys.argv[sys.argv.index('--') + 1:]
input_path = argv[0]
output_path = argv[1]
h_angle = float(argv[2]) if len(argv) > 2 else 0
v_angle = float(argv[3]) if len(argv) > 3 and argv[3] != '' else 15
num_frames = int(argv[4]) if len(argv) > 4 else 72
duration = float(argv[5]) if len(argv) > 5 else 3.0

scene = bpy.context.scene
view_layer = bpy.context.view_layer

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(confirm=False)

bpy.ops.import_scene.gltf(filepath=input_path)

view_layer.update()
coords = []
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bbox = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
        coords.extend(bbox)

if coords:
    min_x = min(v.x for v in coords)
    max_x = max(v.x for v in coords)
    min_y = min(v.y for v in coords)
    max_y = max(v.y for v in coords)
    min_z = min(v.z for v in coords)
    max_z = max(v.z for v in coords)
    center = mathutils.Vector((
        (min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2,
    ))
    size = max(max_x - min_x, max_y - min_y, max_z - min_z)
else:
    center = mathutils.Vector((0, 0, 0))
    size = 1.0

dist = size * 1.5
cam_data = bpy.data.cameras.new('Camera')
cam_obj = bpy.data.objects.new('Camera', cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

h_rad = math.radians(h_angle)
v_rad = math.radians(v_angle)
radius = dist * math.sqrt(0.5**2 + 1.0**2 + 0.3**2)
dx = radius * math.cos(v_rad) * math.sin(h_rad)
dy = -radius * math.cos(v_rad) * math.cos(h_rad)
dz = radius * math.sin(v_rad)
cam_obj.location = center + mathutils.Vector((dx, dy, dz))

target = bpy.data.objects.new('Target', None)
scene.collection.objects.link(target)
target.location = center
track = cam_obj.constraints.new(type='TRACK_TO')
track.target = target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.ops.object.light_add(type='SUN', location=(5, 10, 7))
sun = bpy.context.active_object
sun.data.energy = 5

bpy.ops.object.light_add(type='SUN', location=(-5, -5, 5))
fill = bpy.context.active_object
fill.data.energy = 1.5

turntable = bpy.data.objects.new('Turntable', None)
turntable.location = center
scene.collection.objects.link(turntable)

for obj in list(bpy.data.objects):
    if obj.type == 'MESH':
        obj.parent = turntable

rot_per_frame = 360.0 / num_frames
for i in range(num_frames):
    frame = i + 1
    angle = math.radians(rot_per_frame * i)
    turntable.rotation_euler = (0, 0, angle)
    turntable.keyframe_insert(data_path='rotation_euler', frame=frame)

scene.frame_start = 1
scene.frame_end = num_frames

fps = round(num_frames / duration)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.render.use_overwrite = True

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
