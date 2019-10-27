# Within Blender, run the specified command
import sys
import bpy
import argparse
 
def parse_args():
    my_args = sys.argv[sys.argv.index('--') + 1:]

    parser = argparse.ArgumentParser('Run Blender and render animation')
    parser.add_argument('-S', '--scene', required=False, type=str, default="Scene")
    parser.add_argument('-x', '--xres', required=False, type=int, default=1920)
    parser.add_argument('-y', '--yres', required=False, type=int, default=1080)
    parser.add_argument('-p', '--percentage', required=False, type=int, default=100)
    parser.add_argument('-r', '--renderer', required=False, type=str, default='CYCLES')
    parser.add_argument('-s', '--samples', required=True, type=int)
    parser.add_argument('-t', '--step', required=False, type=int, default=1)
    parser.add_argument('-c', '--compositing', required=False, type=bool, default=True)
    parser.add_argument('-f', '--startframe', required=False, type=int, default=-1)
    parser.add_argument('-e', '--endframe', required=False, type=int, default=-1)
    parser.add_argument('-b', '--blend', required=False, type=str, default=None)
    parser.add_argument('-o', '--output', required=False, type=str, default=None)
    
    return parser.parse_args(my_args)

def enable_cuda_devices():
    prefs = bpy.context.preferences
    cprefs = prefs.addons['cycles'].preferences
    cprefs.get_devices()

    # Attempt to set GPU device types if available
    for compute_device_type in ('CUDA', 'OPENCL', 'NONE'):
        try:
            cprefs.compute_device_type = compute_device_type
            print("Compute device selected: {0}".format(compute_device_type))
            break
        except TypeError:
            pass

    # Any CUDA/OPENCL devices?
    acceleratedTypes = ['CUDA', 'OPENCL']
    accelerated = any(device.type in acceleratedTypes for device in cprefs.devices)
    print('Accelerated render = {0}'.format(accelerated))

    # If we have CUDA/OPENCL devices, enable only them, otherwise enable
    # all devices (assumed to be CPU)
    print(cprefs.devices)
    for device in cprefs.devices:
        device.use = not accelerated or device.type in acceleratedTypes
        print('Device enabled ({type}) = {enabled}'.format(type=device.type, enabled=device.use))

def do_run_process():
    args = parse_args()
    
    enable_cuda_devices()

    scene = bpy.context.scene

    scene.render.engine = args.renderer
    scene.render.resolution_percentage = args.percentage
    scene.render.resolution_x = args.xres
    scene.render.resolution_y = args.yres
    scene.render.use_compositing = True if args.compositing is None else args.compositing
    scene.render.filepath = args.output if args.output else '/tmp/render_output/'
    scene.render.tile_x = 256
    scene.render.tile_y = 256
    
    scene.frame_step = args.step
    scene.frame_start = args.startframe if args.startframe >= 1 else scene.frame_start
    scene.frame_end = args.endframe if args.endframe >= 1 else scene.frame_end

    scene.cycles.samples = args.samples
    scene.cycles.device = 'GPU'

    bpy.ops.render.render(animation=True)
    
do_run_process()