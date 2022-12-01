import asyncio
import websockets
import websockets.exceptions
import cv2
from phone_finder import ImageHandler as IH
from multiprocessing.pool import ThreadPool
from collections import deque
from get_video_frame_webcam import Camera
import time


class WebSocketServer:

    def __init__(self, host, port):
        self._server = websockets.serve(self._start, host, port)

    def start(self):
        asyncio.get_event_loop().run_until_complete(self._server)
        asyncio.get_event_loop().run_forever()

    async def _start(self, websocket, path):
        camera = Camera(0)
        camera.start()

        img_handler = IH("PhoneCam")
        threads = 4
        pool = ThreadPool(processes=threads)
        pending = deque()
        print(f"Connected from path ={path}")
        res_img = None
        running = True

        # acquisition image: num is the image number
        while running:
            while len(pending) > 0 and pending[0].ready():
                thresh, res_img, markers = pending.popleft().get()
                try:
                    await websocket.send(str(time.time()))
                except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosed):
                    running = False
                self.fit_to_screen('video', res_img)

            if len(pending) < threads:
                frame = camera.frame
                task = pool.apply_async(img_handler.find_phone, (frame.copy(),))
                pending.append(task)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                running = False
            if key & 0xFF == ord('s'):
                cv2.imwrite("image_{0}.png".format(time.time()), res_img)
        camera.stop()
        cv2.destroyAllWindows()

    def fit_to_screen(self, name, img):
        dim = (int(img.shape[1] * 2), int(img.shape[0] * 2))
        cv2.imshow(name, cv2.resize(img, dim, cv2.INTER_AREA))

