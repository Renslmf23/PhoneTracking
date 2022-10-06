import numpy as np
import cv2
from


def main():
    vid = cv2.VideoCapture(0)
    while True:
        ret, frame = vid.read()
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    main()
