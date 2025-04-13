#!/usr/bin/env python3

import pyrealsense2 as rs
import cv2
import numpy as np

def main():
    #---------------------------------------------
    # 1. Setup RealSense Pipeline
    #---------------------------------------------
    pipeline = rs.pipeline()
    config = rs.config()

    # Configure the pipeline to stream color
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)

    #---------------------------------------------
    # 2. Load (or define) Camera Calibration
    #---------------------------------------------
    # If you have a saved .npz file from calibration with 'camera_matrix' and 'dist_coeffs':
    # Example: np.savez('camera_calib.npz', camera_matrix=mtx, dist_coeffs=dist)
    # data = np.load('camera_calib.npz')
    # camera_matrix = data['camera_matrix']
    # dist_coeffs = data['dist_coeffs']

    # Otherwise, define them directly (placeholder values shown below):
    # (Replace with real calibration values!)
    camera_matrix = np.array([[615.0,   0.0, 320.0],
                              [  0.0, 615.0, 240.0],
                              [  0.0,   0.0,   1.0]], dtype=np.float32)
    dist_coeffs   = np.zeros((5, 1), dtype=np.float32)  # or your actual distortion

    #---------------------------------------------
    # 3. Create ArUco Dictionary and Parameters
    #---------------------------------------------
    aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
    aruco_params = cv2.aruco.DetectorParameters_create()

    # Adjust any detector parameters as needed
    # aruco_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX

    #---------------------------------------------
    # 4. Main Loop for Frame Capture + Detection
    #---------------------------------------------
    try:
        while True:
            # Wait for a coherent pair of frames: depth (unused) and color
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue

            # Convert to numpy array
            color_image = np.asanyarray(color_frame.get_data())

            # Optional: resize or process color_image here if desired
            # color_image = cv2.resize(color_image, (640, 480))

            # Convert to grayscale for detection
            gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

            # 4a. Detect ArUco markers
            corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)

            # If markers are detected
            if ids is not None:
                # Draw marker boundaries and IDs
                cv2.aruco.drawDetectedMarkers(color_image, corners, ids)

                # 4b. Pose Estimation (Optional) - if you want to see axes on each marker
                marker_length = 0.05  # 5 cm as an example; set based on your actual marker size
                rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                    corners, marker_length, camera_matrix, dist_coeffs
                )

                for i, marker_id in enumerate(ids):
                    # Draw 3D axes on each marker
                    rvec = rvecs[i][0]
                    tvec = tvecs[i][0]
                    cv2.aruco.drawAxis(color_image, camera_matrix, dist_coeffs, rvec, tvec, 0.03)

                    # Optionally put text with ID/position
                    c = corners[i][0]
                    center_x, center_y = int(c[:,0].mean()), int(c[:,1].mean())
                    cv2.putText(color_image, f"ID {marker_id[0]}", 
                                (center_x - 10, center_y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                0.7, (0,255,0), 2, cv2.LINE_AA)

                    # If you just want to see distance from camera:
                    # for example, Z-distance from tvec
                    distance_z = tvec[2]
                    cv2.putText(color_image, f"Z={distance_z:.2f}m", 
                                (center_x - 10, center_y + 20),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0,255,0), 2, cv2.LINE_AA)

            # Show the image
            cv2.imshow("RealSense ArUco Tracker", color_image)

            # Press ESC or 'q' to exit
            key = cv2.waitKey(1)
            if key & 0xFF in (27, ord('q')):
                break

    finally:
        # Stop streaming
        pipeline.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
