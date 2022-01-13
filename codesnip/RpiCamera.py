"""
How to setup:
# use sudo apt install python3-picamera.
adjust picamera v2 lense focus.
counter-clockwise if near focus, clockwise if further focus. 
max resolution is 3280×2464 
distance between focus plane and camera: 11c. 
"""
import time
import picamera

with picamera.PiCamera() as camera:
    camera.resolution = (3280,2464)
    camera.start_preview()
    # Camera warm-up time
    time.sleep(2)
    camera.capture('foo.jpg')



# capture to PIL
import io
import time
import picamera
from PIL import Image

# Create the in-memory stream
stream = io.BytesIO()
with picamera.PiCamera() as camera:
    camera.start_preview()
    time.sleep(2)
    camera.capture(stream, format='jpeg')
# "Rewind" the stream to the beginning so we can read its content
stream.seek(0)
image = Image.open(stream)


# reize after capture
import time
import picamera

with picamera.PiCamera() as camera:
    camera.resolution = (1024, 768)
    camera.start_preview()
    # Camera warm-up time
    time.sleep(2)
    camera.capture('foo.jpg', resize=(320, 240))

"""
camera.sharpness -100-100 defalt 0
camera.shutter_speed 0 is automatic or shutter_speed in microseconds
camera.iso  100-800
camera.exposure_compensation -25 and 25
camera.contrast 0-100
camera.brightness 0-100, default 50
"""