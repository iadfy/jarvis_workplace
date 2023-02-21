import datetime
from tkinter import *
from PIL import Image, ImageTk, ImageGrab
import socket
import subprocess
import os
import pickle
import numpy as np
import cv2
import threading
import time


class ThirdPartyOperator(threading.Thread):
    def __init__(self, path_text):
        threading.Thread.__init__(self)
        self.path = path_text

    def run(self) -> None:
        os.popen(self.path)


class TkWrapper(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.is_wifi_connected = False
        self.current_img = (False, None)
        self.current_screen = None

        self.config_root()

        self.img_label = Label(self)
        self.img_label.config(relief="ridge")
        self.img_label.grid(row=0, column=0)

        self.logs = Listbox(self, height=30, width=50)
        self.logs.grid(row=0, column=1)
        self.logging("JARVIS 구동 시작")

        self.logging("화면 받아오기 시작")
        self.interface_screen()

        self.after(0, self.init_work)

    def config_root(self):
        self.title("JARVIS")
        self.minsize(1024, 768)

    def update_img_label(self, img):
        self.img_label.config(image=img)
        self.img_label.image = img

    def take_screen(self, start_x=0, start_y=0, width=1920, height=1080):
        screenshot = ImageGrab.grab((start_x, start_y, width, height))
        self.current_screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def show_screen(self):
        self.current_screen = cv2.resize(self.current_screen, (640, 480))
        img = cv2.cvtColor(self.current_screen, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        # img.resize((640, 480))
        tk_screen = ImageTk.PhotoImage(image=img)
        return tk_screen

    def interface_screen(self):
        self.take_screen()
        if self.current_img[0]:
            self.find_target()
        imgtk_screen = self.show_screen()
        self.update_img_label(imgtk_screen)
        self.after(100, self.interface_screen)

    def logging(self, text):
        now = datetime.datetime.now().strftime('%H:%M:%S')
        self.logs.insert(END, "{} {}".format(now, text))

    def check_wifi(self):
        self.logging("Wifi 확인: 8.8.8.8에 접근 시도")
        try:
            # connect to the host -- tells us if the host is actually
            # reachable
            socket.create_connection(("8.8.8.8", 53))
            self.logging("Wifi 연결 확인됨")
            return True
        except OSError:
            pass
        self.logging("Wifi 네트워크 확인 안됨")
        return False

    def take_img(self, img_data_name: str):
        with open(r"D:\jarvis\pickles\{}.imgData".format(img_data_name), 'rb') as f:
            data = pickle.load(f)
        self.current_img = (True, data)

    def find_target(self, threshold=0.95):
        h, w, d = self.current_img[1].shape
        result = cv2.matchTemplate(self.current_screen, self.current_img[1], cv2.TM_CCOEFF_NORMED)
        # cv2.imshow("target", self.current_img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val > threshold:
            x, y = max_loc
            bottom_right = (x + w, y + h)
            cv2.rectangle(self.current_screen, (x, y), bottom_right, (0, 0, 255), 5)

            # cv2.imshow("current", current_screen)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            center = (x + w // 2, y + h // 2)
            return center
        else:
            return None

    def start(self):
        self.mainloop()

    def init_work(self):
        self.is_wifi_connected = self.check_wifi()
        if self.is_wifi_connected:  # not
            self.logging("사내망 wifi 연결 프로그램 구동")
            wifi_manager = ThirdPartyOperator(r"C:\Program Files\Unetsystem\AnyClick\AnyMgm.exe")
            wifi_manager.run()
            self.take_img("wifi_manager")
            pass


if __name__ == '__main__':
    jarvis = TkWrapper()
    jarvis.start()
