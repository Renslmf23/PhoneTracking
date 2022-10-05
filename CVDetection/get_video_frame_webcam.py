from threading import Thread
import cv2


class Camera:
    def __init__(self, camera):
        self.vid = cv2.VideoCapture(camera)
        _, self.frame = self.vid.read()
        self.stopped = False

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            _, self.frame = self.vid.read()

    def stop(self):
        self.stopped = True
        self.vid.release()
        