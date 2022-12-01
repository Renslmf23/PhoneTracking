import cv2
from cv2 import aruco


def create_marker(ids):
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    img = aruco.drawMarker(aruco_dict, ids, 700)
    print(cv2.imwrite(r"C:\Users\rensv\OneDrive - De Haagse Hogeschool\Bedrijf\PhoneTracking\aruco{0}.jpg".format(ids), img))


def find_markers(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    return corners, ids
