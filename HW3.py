import pyrealsense2 as rs
import numpy as np
import cv2
from   picamera2 import Preview
import time
from maestro import Controller

class Tango:
    def __init__(self):
        self.Tango = Controller()


# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
t = Tango()
t.Tango.setTarget(0, 5200)
t.Tango.setTarget(1, 5200)
t.Tango.setTarget(0, 6000)
t.Tango.setTarget(1, 6000)
time.sleep(1)
t.Tango.setTarget(3, 3500)
t.Tango.setTarget(4, 4000)
time.sleep(1)
t.Tango.setTarget(3, 3500)
t.Tango.setTarget(4, 9000)
time.sleep(1)
t.Tango.setTarget(3, 7500)
t.Tango.setTarget(4, 9000)
time.sleep(1)
t.Tango.setTarget(3, 7500)
t.Tango.setTarget(4, 4000)
time.sleep(1)
t.Tango.setTarget(3, 5500)
t.Tango.setTarget(4, 6000)
time.sleep(1)

start_time = time.time()
while (time.time() - start_time < 0.3):
    t.Tango.setTarget(0, 5000)
time.sleep(1)
t.Tango.setTarget(0, 6000)


# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

if device_product_line == 'L500':
    config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
else:
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)


try:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', color_image)
        cv2.waitKey(1)

        #color_image is what we need to use
        high_values = np.array([150, 150, 255])
        low_values = np.array([0, 0, 150])

        size = color_image.shape
        thresh = size[0] * size[1] / 4
        mask = cv2.inRange(color_image, low_values, high_values)
        count = cv2.countNonZero(mask)
        print(count)
        if (count >= size[0] * size[1] / 10):
            cv2.destroyAllWindows()
            break
    time.sleep(5)
    start_time = time.time()
    while (time.time() - start_time < 4):
        t.Tango.setTarget(1, 5200)

    t.Tango.setTarget(1, 6000)
    exit(0)

finally:
    pipeline.stop()

