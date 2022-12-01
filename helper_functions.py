import numpy as np
import cv2
import math


class Box:
    def __init__(self, cv_rect):
        orig_points = cv2.boxPoints(cv_rect)
        orig_points = np.int0(orig_points)
        size_x = math.sqrt((orig_points[1][0] - orig_points[0][0])**2 + (orig_points[1][1] - orig_points[0][1])**2)
        size_y = math.sqrt((orig_points[2][0] - orig_points[1][0])**2 + (orig_points[2][1] - orig_points[1][1])**2)
        self.points = orig_points.copy()
        if size_x > size_y:
            self.points[1] = orig_points[3]
            self.points[3] = orig_points[1]

    def get_mid_line(self):
        bottom_line = Line(self.points[0], self.points[1])
        top_line = Line(self.points[2], self.points[3])
        return Line(bottom_line.midpoint(), top_line.midpoint())


class Line:
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2

    def midpoint(self):
        return int(self.point1[0] + (self.point2[0] - self.point1[0])/2), int(self.point1[1] + (self.point2[1] - self.point1[1])/2)

    def points(self):
        return [self.point1, self.point2]

    def get_angle(self):
        return math.degrees(math.atan2((self.point2[1] - self.point1[1]), (self.point2[0] - self.point1[0]))) + 90

    def lowest_point(self):
        if self.point1[1] < self.point2[1]:
            return self.point2
        else:
            return self.point1

    def highest_point(self):
        if self.point1[1] > self.point2[1]:
            return self.point2
        else:
            return self.point1

    def left_point(self):
        if self.point1[0] < self.point2[0]:
            return self.point1
        else:
            return self.point2

    def right_point(self):
        if self.point1[0] > self.point2[0]:
            return self.point1
        else:
            return self.point2

    def extend_down(self, distance):
        point1, point2 = self.point1, self.point2
        if self.point1[1] > self.point2[1]:
            point1 = self.point2
            point2 = self.point1
        lenAB = math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)
        point3 = [0, 0]
        point3[0] = point2[0] + (point2[0] - point1[0]) / lenAB * distance
        point3[1] = point2[1] + (point2[1] - point1[1]) / lenAB * distance
        return point3

    def all_points_right_of_value(self, value):
        if self.point1[0] > value and self.point2[0] > value:
            return True
        else:
            return False

    def get_length(self):
        return math.sqrt((self.point1[0]-self.point2[0])**2 + (self.point1[1]-self.point2[1])**2)


def unwarp_calib(img, src, dst):
    h, w = img.shape[:2]
    # use cv2.getPerspectiveTransform() to get M, the transform matrix, and Minv, the inverse
    M = cv2.getPerspectiveTransform(src, dst)
    # use cv2.warpPerspective() to warp your image to a top-down view
    warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)
    return warped, M


def unwarp(img, m):
    h, w = img.shape[:2]
    return cv2.warpPerspective(img, m, (w, h), flags=cv2.INTER_LINEAR)