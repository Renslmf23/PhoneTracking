import gxipy as gx
from threading import Thread


class CamManager:
    def __init__(self):
        # create a device manager
        self.device_manager = gx.DeviceManager()
        dev_num, dev_info_list = self.device_manager.update_device_list()
        if dev_num == 0:
            print("No cameras found!")
            return

    def get_camera(self, id):
        return Camera(self.device_manager.open_device_by_user_id(id)).start()


class Camera:
    def __init__(self, camera):
        self.camera = camera
        self.camera.TriggerMode.set(gx.GxSwitchEntry.OFF)
        self.camera.ExposureTime.set(20000.0)
        self.camera.Gain.set(14.0)
        self.camera.BalanceWhiteAuto.set(gx.GxAutoEntry.CONTINUOUS)
        # print(self.camera.Height.get())
        # self.camera.Height.set(int(1536*0.6))
        # self.camera.Width.set(int(2048*0.6)))
        self.camera.stream_on()
        self.frame = self.camera.data_stream[0].get_image().convert("RGB").get_numpy_array()[:, :, ::-1]
        self.stopped = False

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            self.frame = self.camera.data_stream[0].get_image().convert("RGB").get_numpy_array()[:, :, ::-1]

    def stop(self):
        self.stopped = True
        self.camera.stream_off()
        self.camera.close_device()