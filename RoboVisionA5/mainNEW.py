from operator import truediv
import cv2 as cv
import numpy as np
import time
from maestro import Controller
import serial
from sys import version_info
import pyrealsense2 as rs
from picamera2 import Preview

class Tango:
    def __init__(self):
        self.Tango = Controller()

class Marker:
    markerDict = {}

    def __init__(self, marker_id):
        self.marker_id = marker_id
        self.globalPosition = (3, 0, 3)
        self.relativeDistance = (0.0, 0.0, 0.0)
        Marker.markerDict[marker_id] = self

    def updateRelativeDistance(self, triple):
        updateLR = self.globalPosition[0] - triple[0]
        updateUD = self.globalPosition[1] - triple[1]
        updateDist = self.globalPosition[2] - triple[2]
        self.relativeDistance = (updateLR, updateUD, updateDist)
        return self.relativeDistance

    @classmethod
    def updateMarker(cls, marker_id):
        if marker_id not in cls.markerDict:
            cls.markerDict[marker_id] = Marker(marker_id)
        return cls.markerDict[marker_id]


tango = None

def pnp_feet_conversion(tvec):
    # Tidy this up so we directly compute from tvec[0], tvec[1], tvec[2].
    leftRight = (0.16 - tvec[0]) / 0.168
    upDown   = (0.0556 - tvec[1]) / 0.168
    depth    = (0.00051 - tvec[2]) / 0.0002
    return (leftRight, upDown, depth)

def move_forwards_to_marker(distance, tango):
    while distance >= 2:
        tango.Tango.setTarget(0, 5200)
        # Recompute distance or break condition here if needed.
    tango.Tango.setTarget(0, 6000)

def move_backwards(distance, tango):
    while distance >= 2:
        tango.Tango.setTarget(0, 6800)
        # Recompute distance or break condition here if needed.
    tango.Tango.setTarget(0, 6000)

def move_forwards(durationordistance, tango):
    start_time = time.time()
    while (time.time() - start_time < durationordistance):
        tango.Tango.setTarget(0, 6800)
        time.sleep(0.01)
    tango.Tango.setTarget(0,6000)

def turn(markerID, tango):
    """
    Turns and moves in a pattern based on whether markerID is even or odd.
    Adjust these movements as needed for your actual robot logic.
    """
    if (markerID % 2 == 0):  # even
        # Turn right
        start_time = time.time()
        while (time.time() - start_time < 1):
            tango.Tango.setTarget(1, 5200)
            time.sleep(0.01)
        tango.Tango.setTarget(1, 6000)
        # Forward 1
        move_forwards(1, tango)
        # Turn left
        start_time = time.time()
        while (time.time() - start_time < 1):
            tango.Tango.setTarget(1, 6800)
            time.sleep(0.01)
        tango.Tango.setTarget(1, 6000)
        # Forward 2
        move_forwards(2, tango)
        # Turn left
        start_time = time.time()
        while (time.time() - start_time < 1):
            tango.Tango.setTarget(1, 6800)
            time.sleep(0.01)
        tango.Tango.setTarget(1, 6000)
        # Forward 1
        move_forwards(1, tango)
        # Turn right
        start_time = time.time()
        while (time.time() - start_time < 1):
            tango.Tango.setTarget(1, 5200)
            time.sleep(0.01)
        tango.Tango.setTarget(1, 6000)
    else:  # odd
        # Turn left
        start_time = time.time()
        while (time.time() - start_time < 1):
            tango.Tango.setTarget(1, 6800)
            time.sleep(0.01)
        tango.Tango.setTarget(1, 6000)
        # Forward 1
        move_forwards(1, tango)
        # Turn right
        start_time = time.time()
        while (time.time() - start_time < 1):
            tango.Tango.setTarget(1, 5200)
            time.sleep(0.01)
        tango.Tango.setTarget(1, 6000)
        # Forward 2
        move_forwards(2, tango)
        # Turn right
        start_time = time.time()
        while (time.time() - start_time < 1):
            tango.Tango.setTarget(1, 5200)
            time.sleep(0.01)
        tango.Tango.setTarget(1, 6000)
        # Forward 1
        move_forwards(1, tango)
        # Turn left
        start_time = time.time()
        while (time.time() - start_time < 1):
            tango.Tango.setTarget(1, 6800)
            time.sleep(0.01)
        tango.Tango.setTarget(1, 6000)

def main():
    global tango
    tango = Tango()
    # Initialize motors
    tango.Tango.setTarget(0, 5200)
    tango.Tango.setTarget(1, 5200)
    tango.Tango.setTarget(0, 6000)
    tango.Tango.setTarget(1, 6000)
    time.sleep(1)

    # --------------------------------------------------------------------
    # RealSense configuration (same approach as denoviewer)
    # --------------------------------------------------------------------
    pipeline = rs.pipeline()
    config   = rs.config()

    # Resolve the device and product line
    pipeline_wrapper  = rs.pipeline_wrapper(pipeline)
    pipeline_profile  = config.resolve(pipeline_wrapper)
    device            = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs.camera_info.product_line))

    found_rgb = False
    for s in device.sensors:
        if s.get_info(rs.camera_info.name) == 'RGB Camera':
            found_rgb = True
            break
    if not found_rgb:
        print("The demo requires Depth camera with Color sensor")
        exit(0)

    # Enable depth
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    # Check if device is L500
    if device_product_line == 'L500':
        config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
    else:
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)

    # --------------------------------------------------------------------
    # ArUco detection setup
    # --------------------------------------------------------------------
    # If your OpenCV is older, you might use DetectorParameters_create().
    arucoDict   = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
    arucoParams = cv.aruco.DetectorParameters_create()

    # Dummy camera matrix for solvePnP (no lens distortion)
    focal_length = 1.0
    center       = (640 // 2, 480 // 2)
    camera_matrix = np.array([
        [focal_length,   0,          center[0]],
        [0,              focal_length, center[1]],
        [0,              0,             1       ]
    ], dtype="double")
    dist_coeffs   = np.zeros((4, 1))

    cv.namedWindow('color_frame', cv.WINDOW_AUTOSIZE)
    cv.namedWindow('depth_colormap', cv.WINDOW_AUTOSIZE)

    try:
        while True:
            frames      = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            if not depth_frame or not color_frame:
                continue

            # Convert images to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Create a depth colormap for display (optional)
            depth_colormap = cv.applyColorMap(
                cv.convertScaleAbs(depth_image, alpha=0.03),
                cv.COLORMAP_JET
            )

            # -------------------------------------------------------------
            # ArUco detection on color_image
            # -------------------------------------------------------------
            grayFrame = cv.cvtColor(color_image, cv.COLOR_BGR2GRAY)
            (corners, ids, rejected) = cv.aruco.detectMarkers(grayFrame, arucoDict, parameters=arucoParams)

            # If markers detected, proceed:
            if ids is not None and len(corners) > 0:
                ids = ids.flatten()
                for (markerCorner, markerID) in zip(corners, ids):
                    # Reshape corner points
                    corner_pts = markerCorner.reshape((4, 2))
                    (topLeft, topRight, bottomRight, bottomLeft) = corner_pts

                    topLeft     = (int(topLeft[0]),     int(topLeft[1]))
                    topRight    = (int(topRight[0]),    int(topRight[1]))
                    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                    bottomLeft  = (int(bottomLeft[0]),  int(bottomLeft[1]))

                    # Draw bounding box on color_image
                    cv.line(color_image, topLeft, topRight,     (0, 255, 0), 2)
                    cv.line(color_image, topRight, bottomRight, (0, 255, 0), 2)
                    cv.line(color_image, bottomRight, bottomLeft,(0, 255, 0), 2)
                    cv.line(color_image, bottomLeft, topLeft,    (0, 255, 0), 2)

                    # Marker center
                    cX = int((topLeft[0] + bottomRight[0]) / 2)
                    cY = int((topLeft[1] + bottomRight[1]) / 2)
                    cv.circle(color_image, (cX, cY), 4, (0, 0, 255), -1)

                    # ID text
                    cv.putText(color_image, str(markerID),
                               (topLeft[0], topLeft[1] - 10),
                               cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

                    # PnP Solve
                    L = 0.1  # side length in meters for the marker
                    object_points = np.array([
                        [-L / 2, -L / 2, 0],
                        [ L / 2, -L / 2, 0],
                        [ L / 2,  L / 2, 0],
                        [-L / 2,  L / 2, 0]
                    ], dtype="double")

                    image_points = np.array([topLeft, topRight, bottomRight, bottomLeft], dtype="double")
                    success, rvec, tvec = cv.solvePnP(object_points, image_points, camera_matrix, dist_coeffs)

                    if success:
                        print(f"Detected MarkerID={markerID}, tvec={tvec.ravel()}")
                        triple = pnp_feet_conversion(tvec)

                        # Since markerID is an integer, no need to loop over it:
                        marker_instance = Marker.updateMarker(markerID)
                        new_relative    = marker_instance.updateRelativeDistance(triple)
                        print(f"Marker {markerID} relative distance: {new_relative}")

                        # Example: Move forward if distance is > 1.5
                        flag = False
                        while not flag:
                            if new_relative[2] > 1.5:
                                move_forwards(1, tango)
                                # Recompute or update new_relative if you have a live update:
                                new_relative = marker_instance.updateRelativeDistance(triple)
                                print(f"Marker {markerID} new relative distance: {new_relative}")
                            else:
                                flag = True

                        # Example turning logic
                        turn(markerID, tango)

            # Show frames
            cv.imshow('color_frame', color_image)
            cv.imshow('depth_colormap', depth_colormap)

            # Press 'q' to quit
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        pipeline.stop()
        cv.destroyAllWindows()

if __name__ == '__main__':
    main()
