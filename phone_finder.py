import cv2
import numpy as np
import xml.etree.ElementTree as ET
from helper_functions import Box, Line, unwarp, unwarp_calib
from get_video_frame_webcam import Camera
import markers
from cv2 import aruco

class ImageHandler:
    def __init__(self, cam_name, detect_edge=False):
        self.tree = ET.parse("cam_parameters.xml")
        self.root = self.tree.getroot()
        self.camSetting = None
        for camSettings in self.root.findall("Camera"):
            if camSettings.get("name") == cam_name:
                self.camSetting = camSettings
                break
        if self.camSetting is not None:
            self.kernel_size = int(self.camSetting.find('KernelSize').text)
            self.kernel_size_erosion = int(self.camSetting.find('KernelSizeErosion').text)
            self.kernel_dilation = np.ones((self.kernel_size, self.kernel_size), np.uint8)
            self.kernel_erosion = np.ones((self.kernel_size_erosion, self.kernel_size_erosion), np.uint8)
            hsvParams = self.camSetting.find("HSVParams")
            self.hMin = int(hsvParams.find("hMin").text)
            self.sMin = int(hsvParams.find("sMin").text)
            self.vMin = int(hsvParams.find("vMin").text)
            self.hMax = int(hsvParams.find("hMax").text)
            self.sMax = int(hsvParams.find("sMax").text)
            self.vMax = int(hsvParams.find("vMax").text)
            self.lower = np.array([self.hMin, self.sMin, self.vMin])
            self.upper = np.array([self.hMax, self.sMax, self.vMax])
            self.scale_percent = int(self.camSetting.find("ScalePercent").text)
            self.min_phone_width = int(self.camSetting.find("MinPhoneWidth").text)
            self.max_phone_width = int(self.camSetting.find("MaxPhoneWidth").text)
            self.min_phone_height = int(self.camSetting.find("MinPhoneHeight").text)
            self.max_phone_height = int(self.camSetting.find("MaxPhoneHeight").text)
            self.unwarp_matrix = []
            for col in self.camSetting.find("PerspectiveMatrix").findall("col"):
                col_array = []
                for row in col.findall("row"):
                    col_array.append(float(row.text))
                self.unwarp_matrix.append(col_array)
            self.correct_warp = self.camSetting.find("CorrectWarp").text == "True"
            self.flip = self.camSetting.find("Flip").text == "True"
            self.crop_dist = float(self.camSetting.find("CropDistance").text)
            self.offset = (int(self.camSetting.find("OffsetCamera").find("x").text), int(self.camSetting.find("OffsetCamera").find("y").text))
        self.max_rail_angle_difference = 45  # max difference in degrees between two rails
        self.dist_between_rails_threshold = (60, 300)  # max difference in pixels between two rails
        self.width, self.height = 0, 0  # image width and height in px
        self.smooth_kernel = np.ones((5,5),np.float32)/25

    def display_image(self, images):
        while True:
            id = 0
            if len(images) < 5:
                for image in images:
                    cv2.imshow("Detect" + str(id), image)
                    id += 1
            else:
                cv2.imshow("Detect" + str(id), images)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

    def filter_image(self, img):
        # self.display_image(img)
        if self.flip:
            img = cv2.flip(img, 0)

        self.width = int(img.shape[1])
        self.height = int(img.shape[0])

        # Set minimum and max HSV values to display
        img_sharpened = cv2.filter2D(img, -1, self.smooth_kernel)
        # Create HSV Image and threshold into a range.
        hsv = cv2.cvtColor(img_sharpened, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower, self.upper)
        output = cv2.bitwise_and(img_sharpened, img_sharpened, mask=mask)
        # self.display_image(output)
        gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
        # self.display_image(gray)
        ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        thresh[:int(self.height * self.crop_dist), :] = 0
        # img_dilation = cv2.dilate(thresh, self.kernel_dilation, iterations=1)
        img_erosion = cv2.erode(thresh, self.kernel_erosion, iterations=1)
        img_dilation = cv2.dilate(img_erosion, self.kernel_dilation, iterations=1)
        # self.display_image(img_dilation)
        return img_dilation, img

    def find_phone(self, img):
        # # img = cv2.imread("bezem_v2_cropped.bmp")
        # # return img, img
        filtered, resized = self.filter_image(img)
        contours, hier = cv2.findContours(filtered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:

            rect = cv2.minAreaRect(c)
            size_x, size_y = min(rect[1]), max(rect[1])
            if self.min_phone_width < size_x < self.max_phone_width and self.min_phone_height < size_y < self.max_phone_height:
                epsilon = 0.001 * cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, epsilon, True)
                hull = cv2.convexHull(approx)

                cv2.drawContours(resized, [hull], 0, (0, 255, 0), 1)
                rail = Box(rect)
                # convert all coordinates floating point values to int
                box = rail.points
                cv2.drawContours(resized, [box], 0, (0, 0, 255))
        corners, ids = markers.find_markers(img)
        resized = aruco.drawDetectedMarkers(resized, corners, ids)
        return filtered, resized, corners

    def nothing(self, x):
        pass

    def calib_hsv(self, image=None, cam_num=0):
        if image is None:
            cam = Camera(cam_num)
            cam.start()

        cv2.namedWindow('image')

        # create trackbars for color change
        cv2.createTrackbar('HMin', 'image', 0, 179, self.nothing)  # Hue is from 0-179 for Opencv
        cv2.createTrackbar('SMin', 'image', 0, 255, self.nothing)
        cv2.createTrackbar('VMin', 'image', 0, 255, self.nothing)
        cv2.createTrackbar('HMax', 'image', 0, 179, self.nothing)
        cv2.createTrackbar('SMax', 'image', 0, 255, self.nothing)
        cv2.createTrackbar('VMax', 'image', 0, 255, self.nothing)
        cv2.createTrackbar('KernelDilation', 'image', 0, 10, self.nothing)
        cv2.createTrackbar('KernelErosion', 'image', 0, 10, self.nothing)

        # Set default value for MAX HSV trackbars.
        cv2.setTrackbarPos('HMin', 'image', self.hMin)
        cv2.setTrackbarPos('SMin', 'image', self.sMin)
        cv2.setTrackbarPos('VMin', 'image', self.vMin)
        cv2.setTrackbarPos('HMax', 'image', self.hMax)
        cv2.setTrackbarPos('SMax', 'image', self.sMax)
        cv2.setTrackbarPos('VMax', 'image', self.vMax)
        cv2.setTrackbarPos('KernelDilation', 'image', self.kernel_size)
        cv2.setTrackbarPos('KernelErosion', 'image', self.kernel_size_erosion)
        if self.camSetting is not None:
            if image is not None:
                img_to_check = image
            while 1:
                if image is None:
                    img_to_check = cam.frame
                self.hMin = cv2.getTrackbarPos('HMin', 'image')
                self.sMin = cv2.getTrackbarPos('SMin', 'image')
                self.vMin = cv2.getTrackbarPos('VMin', 'image')

                self.hMax = cv2.getTrackbarPos('HMax', 'image')
                self.sMax = cv2.getTrackbarPos('SMax', 'image')
                self.vMax = cv2.getTrackbarPos('VMax', 'image')
                self.lower = np.array([self.hMin, self.sMin, self.vMin])
                self.upper = np.array([self.hMax, self.sMax, self.vMax])

                self.kernel_size = cv2.getTrackbarPos('KernelDilation', 'image')
                self.kernel_size_erosion = cv2.getTrackbarPos('KernelErosion', 'image')
                self.kernel_dilation = np.ones((self.kernel_size, self.kernel_size), np.uint8)
                self.kernel_erosion = np.ones((self.kernel_size_erosion, self.kernel_size_erosion), np.uint8)
                filtered, resized, _ = self.find_phone(img_to_check)
                cv2.imshow("Result:", filtered)
                cv2.imshow('image', cv2.resize(resized, (int(filtered.shape[1]/2), int(filtered.shape[0]/2)), cv2.INTER_AREA))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cam.stop()
                    cv2.destroyAllWindows()
                    break

            hsvParams = self.camSetting.find("HSVParams")
            hsvParams.find("hMin").text = str(self.hMin)
            hsvParams.find("sMin").text = str(self.sMin)
            hsvParams.find("vMin").text = str(self.vMin)
            hsvParams.find("hMax").text = str(self.hMax)
            hsvParams.find("sMax").text = str(self.sMax)
            hsvParams.find("vMax").text = str(self.vMax)
            self.camSetting.find("KernelSize").text = str(self.kernel_size)
            self.camSetting.find("KernelSizeErosion").text = str(self.kernel_size_erosion)

            self.tree.write('cam_parameters.xml')
            print("Saved!")


if __name__ == "__main__":
    # numpy_image = cv2.imread("2022-06-23_14_57_51_353.bmp")
    img_handler = ImageHandler("PhoneCam")
    img_handler.calib_hsv(cam_num=0)
    # img_handler.calib_hsv(cam_num="1")
    #thres, image, _ = img_handler.find_rails(numpy_image)
    #img_handler.display_image((thres, image))
    # #