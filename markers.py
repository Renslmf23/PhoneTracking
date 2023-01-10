import cv2
from cv2 import aruco


def create_marker(ids):
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    img = aruco.drawMarker(aruco_dict, ids, 700)
    print(cv2.imwrite(r"C:\Users\rensv\OneDrive - De Haagse Hogeschool\Bedrijf\PhoneTracking\aruco{0}.jpg".format(ids), img))


def midpoint_of_four_points(corner):
    centerX = (corner[0][0] + corner[1][0] + corner[2][0] + corner[3][0]) / 4
    centerY = (corner[0][1] + corner[1][1] + corner[2][1] + corner[3][1]) / 4
    return [int(centerX), int(centerY)]
    # if missing_corner == 1 or missing_corner == 4:
    #     for i in range(len(ids)):
    #         if ids[i] == 3 or ids[i] == 0:
    #             mirror_point = midpoints[i]
    #         if ids[i] == 2:
    #             line_point_1 = midpoints[i]
    #         if ids[i] == 1:
    #             line_point_2 = midpoints[i]
    # if missing_corner == 2 or missing_corner == 3:
    #     for i in range(len(ids)):
    #         if ids[i] == 1 or ids[i] == 2:
    #             mirror_point = midpoints[i]
    #         if ids[i] == 3:
    #             line_point_1 = midpoints[i]
    #         if ids[i] == 0:
    #             line_point_2 = midpoints[i]

def find_missing_corner(midpoints, ids):
    #   0               1
    #
    #
    #   2               3
    missing_corner = 10  # sum of all the (ids+1)
    for i in ids:
        missing_corner -= i + 1
    missing_corner -= 1
    mirror_point, line_point_1, line_point_2 = 0, 0, 0
    predicted_point = [0, 0]
    if missing_corner == 0:
        for i in range(len(ids)):
            if ids[i] == 2:
                predicted_point[0] = midpoints[i][0]
            if ids[i] == 1:
                predicted_point[1] = midpoints[i][1]
    if missing_corner == 1:
        for i in range(len(ids)):
            if ids[i] == 3:
                predicted_point[0] = midpoints[i][0]
            if ids[i] == 0:
                predicted_point[1] = midpoints[i][1]
    if missing_corner == 2:
        for i in range(len(ids)):
            if ids[i] == 0:
                predicted_point[0] = midpoints[i][0]
            if ids[i] == 3:
                predicted_point[1] = midpoints[i][1]
    if missing_corner == 3:
        for i in range(len(ids)):
            if ids[i] == 1:
                predicted_point[0] = midpoints[i][0]
            if ids[i] == 2:
                predicted_point[1] = midpoints[i][1]
    # missing_corner = mirror_point_over_edge(mirror_point, line_point_1, line_point_2)
    missing_corner = predicted_point
    midpoints.append(missing_corner)
    return midpoints


def mirror_point_over_edge(mirror_point, line_point_1, line_point_2):
    dx = line_point_2[0] - line_point_1[0]
    dy = line_point_2[1] - line_point_1[1]
    a = (dx * dx - dy * dy) / (dx * dx + dy * dy)
    b = 2 * dx * dy / (dx * dx + dy * dy)
    x2 = round(a * (mirror_point[0] - line_point_1[0]) + b * (mirror_point[1] - line_point_1[1]) + line_point_1[0])
    y2 = round(b * (mirror_point[0] - line_point_1[0]) - a * (mirror_point[1] - line_point_1[1]) + line_point_1[1])
    return [x2, y2]

def find_markers(frame):
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
    midpoints = [midpoint_of_four_points(corner[0]) for corner in corners]
    if len(midpoints) == 4:
        return midpoints
    elif len(midpoints) == 3:
        return find_missing_corner(midpoints, ids)
    else:
        print("Invalid marker state!")
        return None


