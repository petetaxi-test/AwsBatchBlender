c:
cd "C:\Program Files\Blender Foundation\Blender"

set XRES=1920
set YRES=1080 
set PERCENTAGE=25
set RENDERER=CYCLES 
set SAMPLES=128

set STEP=5

REM ------------------------------------------------------------------------------------

blender -b ^
  "E:\My Documents\Label\Video Production\Phone\Blends\Indoors.blend" ^
    -S "Scene" ^
    --python "C:\dev\BlenderScripts\docker-blender\scripts\do_render.py" ^
    -- --xres %XRES% --yres %YRES% --percentage %PERCENTAGE% --samples %SAMPLES% --step %STEP% ^
    --output "C:/tmp/indoors/"

blender -b ^
  "E:\My Documents\Label\Video Production\Phone\Stage.blend" ^
    -S "Side On" ^
    --python "C:\dev\BlenderScripts\docker-blender\scripts\do_render.py" ^
    -- --xres %XRES% --yres %YRES% --percentage %PERCENTAGE% --samples %SAMPLES% --step %STEP% ^
    --output "C:/tmp/gigsideon/"
    
blender -b ^
  "E:\My Documents\Label\Video Production\Phone\Stage.blend" ^
    -S "Overhead" ^
    --python "C:\dev\BlenderScripts\docker-blender\scripts\do_render.py" ^
    -- --xres %XRES% --yres %YRES% --percentage %PERCENTAGE% --samples %SAMPLES% --step %STEP% ^
    --output "C:/tmp/gigoh/"

blender -b ^
  "E:\My Documents\Label\Video Production\Phone\Stage.blend" ^
    -S "Sideways" ^
    --python "C:\dev\BlenderScripts\docker-blender\scripts\do_render.py" ^
    -- --xres %XRES% --yres %YRES% --percentage %PERCENTAGE% --samples %SAMPLES% --step %STEP% ^
    --output "C:/tmp/gig/"



set STEP=1

REM ------------------------------------------------------------------------------------

blender -b ^
  "E:\My Documents\Label\Video Production\Phone\Blends\Indoors.blend" ^
    -S "Scene" ^
    --python "C:\dev\BlenderScripts\docker-blender\scripts\do_render.py" ^
    -- --xres %XRES% --yres %YRES% --percentage %PERCENTAGE% --samples %SAMPLES% --step %STEP% ^
    --output "C:/tmp/indoors/"

blender -b ^
  "E:\My Documents\Label\Video Production\Phone\Stage.blend" ^
    -S "Side On" ^
    --python "C:\dev\BlenderScripts\docker-blender\scripts\do_render.py" ^
    -- --xres %XRES% --yres %YRES% --percentage %PERCENTAGE% --samples %SAMPLES% --step %STEP% ^
    --output "C:/tmp/gigsideon/"
    
blender -b ^
  "E:\My Documents\Label\Video Production\Phone\Stage.blend" ^
    -S "Overhead" ^
    --python "C:\dev\BlenderScripts\docker-blender\scripts\do_render.py" ^
    -- --xres %XRES% --yres %YRES% --percentage %PERCENTAGE% --samples %SAMPLES% --step %STEP% ^
    --output "C:/tmp/gigoh/"

blender -b ^
  "E:\My Documents\Label\Video Production\Phone\Stage.blend" ^
    -S "Sideways" ^
    --python "C:\dev\BlenderScripts\docker-blender\scripts\do_render.py" ^
    -- --xres %XRES% --yres %YRES% --percentage %PERCENTAGE% --samples %SAMPLES% --step %STEP% ^
    --output "C:/tmp/gig/"

