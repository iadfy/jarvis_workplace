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
import pyautogui as at
import queue


class ThirdPartyOperator(threading.Thread):
    def __init__(self, path_text):
        threading.Thread.__init__(self)
        self.path = path_text

    def run(self) -> None:
        os.popen(self.path)


class AutomationOperator(threading.Thread):
    def __init__(self, root):
        threading.Thread.__init__(self)
        self.root = root

    def run(self):
        while True:
            try:
                x, y = self.root.target_point
                if x == -1 and y == -1:
                    at.click()
                else:
                    at.moveTo(x, y)
            except:
                time.sleep(3)


class TkWrapper(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.is_wifi_connected = False

        self.current_img = (False, None)
        self.current_screen = None

        self.target_img = (None, (0, 0))
        self.target_point = (None, None)

        # region 자동화 쓰레드
        self.operator = AutomationOperator(self)
        self.operator.start()
        # endregion

        self.config_root()

        # region 레이아웃 선언
        self.img_label = Label(self)
        self.img_label.config(relief="ridge")
        self.img_label.grid(row=0, column=0)

        self.logs = Listbox(self, height=30, width=50)
        self.logs.grid(row=0, column=1)

        self.target_label = Label(self, relief="solid")
        self.target_label.grid(row=1, column=0)
        self.current_label = Label(self, relief="solid")
        self.current_label.grid(row=1, column=1)
        # endregion

        self.logging("JARVIS 구동 시작")

        self.logging("화면 받아오기 시작")
        self.check_routine()

        self.after(0, self.init_work)

    def config_root(self):
        self.title("JARVIS")
        self.geometry("1024x768+1920+0")
        # self.minsize(1024, 768)

    def update_img_label(self, img: ImageTk):
        self.img_label.config(image=img)
        self.img_label.image = img

    def set_target_img(self, img_data_name: str, config_target: tuple):
        with open(r"D:\jarvis\pickles\{}.imgData".format(img_data_name), 'rb') as f:
            data = pickle.load(f)
        self.target_img = (data, config_target)

    def find_target(self, threshold=0.95):
        # current_img: target
        # current_screen: background
        h, w, d = self.target_img[0].shape
        result = cv2.matchTemplate(self.current_screen, self.target_img[0], cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val > threshold:
            x, y = max_loc
            bottom_right = (x + w, y + h)
            cv2.rectangle(self.current_screen, (x, y), bottom_right, (0, 0, 255), 5)
            center = (x + w // 2, y + h // 2)
            self.target_point = (center[0] + self.target_img[1][0], center[1] + self.target_img[1][1])
            self.logging("타겟 좌표 설정")
            self.target_img = (None, (0, 0))
        #     return center
        # else:
        #     return None

    def bring_screen(self, start_x=0, start_y=0, width=1920, height=1080):
        screenshot = ImageGrab.grab((start_x, start_y, width, height))
        self.current_screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def convert_screen(self):
        self.current_screen = cv2.resize(self.current_screen, (640, 480))
        img = cv2.cvtColor(self.current_screen, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        tk_screen = ImageTk.PhotoImage(image=img)
        return tk_screen

    def check_routine(self):
        self.bring_screen()

        if self.target_img[0] is not None:
            self.find_target()

        # 현재좌표와 타겟좌표가 다르면 그쪽으로 이동
        if self.target_point[0] is not None and self.target_point[1] is not None:
            if at.position().x == self.target_point[0] and at.position().y == self.target_point[1]:
                self.target_point = (None, None)
                self.target_img = (None, (0, 0))
                self.logging("이동 완료")

        self.update_img_label(self.convert_screen())

        self.current_label.config(text="{}, {}".format(at.position().x, at.position().y))
        self.target_label.config(text="{}, {}".format(self.target_point[0], self.target_point[1]))

        self.after(100, self.check_routine)

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

    def start(self):
        self.mainloop()

    def init_work(self):
        self.is_wifi_connected = self.check_wifi()
        if self.is_wifi_connected:  # not
            self.logging("사내망 wifi 연결 프로그램 구동")
            wifi_manager = ThirdPartyOperator(r"C:\Program Files\Unetsystem\AnyClick\AnyMgm.exe")
            wifi_manager.run()
            self.set_target_img("wifi_manager", (-65, -120))
            self.after(1000, None)
            self.target_point = (-1, -1)


if __name__ == '__main__':
    jarvis = TkWrapper()
    jarvis.start()
