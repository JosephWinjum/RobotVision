import cv2 as cv
import numpy as np
import time

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


      #  def moveRotation(self, modula number):
     #   if modula number is even:
      #      turn right
      ##      move a bit
       #     turn left
       #     move past marker
       #     turn left
       ##     move a bit
        #    turn right and face new marker
       # if modula number is odd:
       #     turn left
       #     move a bit
       #     turn right
       #     move past marker
       ###     turn tight
        #    move a bit
        #    turn left and face new marker

    #def move(self, distance param):
    #move forward for (distance param) time





def pnp_feet_conversion(tvec):
    for x in tvec:
        leftRight = (0.16 - tvec[0]) / 0.168
        upDown = (0.0556 - tvec[1]) / .168
        depth = (0.00051 - tvec[2]) / 0.0002
    return (leftRight, upDown, depth)


def main():
    #default stuff - no camera calibration needed??
    arucoDict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
    arucoParams = cv.aruco.DetectorParameters()

    # Camera matrix (example with focal length 1 and image center)
    focal_length = 1.0
    center = (640 // 2, 480 // 2)  # Assuming a 640x480 image
    camera_matrix = np.array([[focal_length, 0, center[0]],
                              [0, focal_length, center[1]],
                              [0, 0, 1]], dtype="double")

    # Assume no lens distortion (simplified case)
    dist_coeffs = np.zeros((4, 1))  # No distortion



    capture = cv.VideoCapture(0)
    cv.namedWindow('frame')
    cv.namedWindow('aruco')
    count = 0
    while(True):
        count += 1;
        status, frame = capture.read()
        grayFrame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        (corners, ids, rejected) = cv.aruco.detectMarkers(grayFrame, arucoDict, parameters=arucoParams)

        if len(corners) > 0:
            ids = ids.flatten()

            for(markerCorner, markerID) in zip(corners, ids):
                corners = markerCorner.reshape(4, 2)
                (topLeft, topRight, bottomRight, bottomLeft) = corners

                topRight = (int(topRight[0]), int(topRight[1]))
                bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                topLeft = (int(topLeft[0]), int(topLeft[1]))

                #surrounding box of marker
                cv.line(frame, topLeft, topRight, (0, 255, 0), 8)
                cv.line(frame, topRight, bottomRight, (0, 255, 0), 8)
                cv.line(frame, bottomRight, bottomLeft, (0, 255, 0), 8)
                cv.line(frame, bottomLeft, topLeft, (0, 255, 0), 8)

                #center of marker
                cX = int((topLeft[0] + bottomRight[0]) / 2)
                cY = int((topLeft[1] + bottomRight[1]) / 2)
                cv.circle(frame, (cX, cY), 4, (0, 0, 255), 2)

                #ID of marker
                cv.putText(frame, str(markerID), (topLeft[0], topLeft[1] - 15),cv.FONT_HERSHEY_SIMPLEX, 2.0, (0, 255, 0), 2)

                L = 0.1  # Side length in meters
                object_points = np.array([
                    [-L / 2, -L / 2, 0],
                    [L / 2, -L / 2, 0],
                    [L / 2, L / 2, 0],
                    [-L / 2, L / 2, 0]
                ], dtype="double")

                # 2D image points from detected corners
                image_points = np.array([
                    topLeft, topRight, bottomRight, bottomLeft
                ], dtype="double")

                # Solve PnP
                success, rvec, tvec = cv.solvePnP(object_points, image_points, camera_matrix, dist_coeffs)

                if success:
                    # Draw the 3D axis (if needed, for visualization)
                    axis = np.float32([[0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]]).reshape(-1, 3)
                    imgpts, _ = cv.projectPoints(axis, rvec, tvec, camera_matrix, dist_coeffs)

                    # Convert imgpts to integer tuples before drawing the lines
                    imgpts = np.int32(imgpts).reshape(-1, 2)  # Convert to integer and reshape

                    # Draw the 3D axis lines
                    #frame = cv.line(frame, tuple(image_points[0].ravel()), tuple(imgpts[0]), (255, 0, 0), 5)
                    #frame = cv.line(frame, tuple(image_points[0].ravel()), tuple(imgpts[1]), (0, 255, 0), 5)
                    #frame = cv.line(frame, tuple(image_points[0].ravel()), tuple(imgpts[2]), (0, 0, 255), 5)


                    # Optional: Output rvec and tvec for debugging
                    if(count % 30 == 0):
                        print(f"Translation Vector: {tvec}")
                        triple = pnp_feet_conversion(tvec)
                        marker_instance = Marker.updateMarker(markerID)
                        new_relative = marker_instance.updateRelativeDistance(triple)
                        print(f"marker id and dist: {markerID}: {new_relative}")


        #show frame
        cv.imshow('aruco', grayFrame)
        cv.imshow('frame', frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv.destroyAllWindows()







if __name__ == '__main__':
    main()

