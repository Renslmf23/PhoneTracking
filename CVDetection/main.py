import cv2
from phone_finder import ImageHandler as IH
from multiprocessing.pool import ThreadPool
from collections import deque
from get_video_frame_webcam import Camera
from helper_functions import Line
import time


def fit_to_screen(name, img):
    dim = (int(img.shape[1] * 0.5), int(img.shape[0] * 0.5))
    cv2.imshow(name, cv2.resize(img, dim, cv2.INTER_AREA))


def main():
    camera = Camera(0)
    camera.start()

    img_handler = IH("PhoneCam")
    threads = 4
    pool = ThreadPool(processes=threads)
    pending = deque()

    time_at_last_process = 0
    process_interval = 0.2

    # acquisition image: num is the image number
    while True:
        while len(pending) > 0 and pending[0].ready():
            thresh, result, midlines = pending.popleft().get()
            fit_to_screen('video', result)

        if len(pending) < threads:
            frame = camera.frame
            task = pool.apply_async(img_handler.find_phone, (frame.copy(),))
            pending.append(task)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            camera.stop()
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
