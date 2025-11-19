import cv2
import numpy as np
import pyzed.sl as sl
import threading
import math

# instantiate with: camera = Camera()
# 
# camera.start() # start capturing the data

# cam_hfov = 101
# cam_vfov = 68

class Camera:
    def __init__(self):
        self.zed = sl.Camera()

        init_params = sl.InitParameters()
        init_params.camera_resolution = sl.RESOLUTION.VGA
        init_params.depth_mode = sl.DEPTH_MODE.ULTRA
        init_params.coordinate_units = sl.UNIT.MILLIMETER

        status = self.zed.open(init_params)
        if status != sl.ERROR_CODE.SUCCESS:
            print("Camera error:", status)
            exit(1)

        camera_info = self.zed.get_camera_information()
        self.width = camera_info.camera_configuration.resolution.width
        self.height = camera_info.camera_configuration.resolution.height

        self.hfov = camera_info.camera_configuration.calibration_parameters.left_cam.h_fov     
        self.vfov = camera_info.camera_configuration.calibration_parameters.left_cam.v_fov
        

        self.runtime = sl.RuntimeParameters()

        self.image = sl.Mat(self.width, self.height, sl.MAT_TYPE.U8_C4, sl.MEM.CPU)
        self.depth = sl.Mat(self.width, self.height, sl.MAT_TYPE.F32_C1, sl.MEM.CPU)

        # These hold the *latest frame* accessible from your main loop
        self.latest_color = None
        self.latest_depth = None

        self.running = False
        self.lock = threading.Lock()

    def _capture_loop(self):
        while self.running:
            if self.zed.grab(self.runtime) == sl.ERROR_CODE.SUCCESS:

                self.zed.retrieve_image(self.image, sl.VIEW.LEFT)
                self.zed.retrieve_measure(self.depth, sl.MEASURE.DEPTH)

                color = self.image.get_data()
                color = cv2.cvtColor(color, cv2.COLOR_BGRA2BGR)
                depth = np.asanyarray(self.depth.get_data())

                # Store frames safely
                with self.lock:
                    self.latest_color = color
                    self.latest_depth = depth

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._capture_loop)
            self.thread.start()

    def stop(self):
        if self.running:
            self.running = False
            self.thread.join()

    def get_frame(self):
        """Returns (color, depth). May return None if first frame not ready."""
        with self.lock:
            return self.latest_color, self.latest_depth
        