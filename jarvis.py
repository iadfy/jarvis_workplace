from tkinter import *
from img import *

import socket
import subprocess
import os
import asyncio

import threading
import time
import datetime
import pyautogui as at
from collections import deque


class ThirdPartyOperator(threading.Thread):
    def __init__(self, path_text):
        threading.Thread.__init__(self)
        self.path = path_text

    def run(self) -> None:
        os.popen(self.path)


class ImageTarget:
    def __init__(self, img_name, adj=(0, 0)):
        self.img: cv2 = set_target_img(img_name)
        self.name = img_name
        self.adj = adj
        self.point = None


class TkWrapper(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.is_wifi_connected: bool = False

        self.operation_q = deque([])

        self.target_img = None

        self.config_layout()

        self.logging("JARVIS 구동 시작")

        self.img_routine()

        self.after(0, self.init_work)

    def config_layout(self):
        self.title("JARVIS")
        self.geometry("1024x768+1920+0")
        # self.minsize(1024, 768)

        # region 레이아웃 선언
        self.img_label = Label(self)
        self.img_label.config(relief="ridge")
        self.img_label.grid(row=0, column=0)

        self.logs = Listbox(self, height=30, width=50)
        self.logs.grid(row=0, column=1)

        self.target_point_guide_label = Label(self)
        self.target_point_guide_label.config(relief="ridge")
        self.target_point_guide_label.grid(row=1, column=0)

        self.target_point_label = Label(self)
        self.target_point_label.config(relief="ridge")
        self.target_point_label.grid(row=1, column=1)

    def logging(self, text):
        now = datetime.datetime.now().strftime('%H:%M:%S')
        self.logs.insert(END, "{} {}".format(now, text))

    def load_img(self, img_name, adj=(0, 0)):
        self.target_img = ImageTarget(img_name, adj)

    def unload_img(self):
        self.target_img = None

    def img_routine(self):
        def update_img_label(img):
            # img: ImgTk
            self.img_label.config(image=img)
            self.img_label.image = img
            return

        # 1. 스크린 이미지 가져오기 -> cv2
        screen: cv2 = bring_screen()

        # 2. 타겟 이미지가 있다면 검색
        if self.target_img:
            cords = find_target(self.target_img.img, screen)

            # 2-1. 타겟 이미지를 찾았으면,
            if cords:
                top_left, (w, h) = cords
                bottom_right = top_left[0] + w, top_left[1] + h

                # 2-1-1. 스크린 이미지에 타겟 윤곽 표시
                mark_rectangular(screen, top_left, bottom_right)

                # 2-1-2. 중심점 및 보정 계산하여 좌표 타겟 설정
                center = (top_left[0] + bottom_right[0]) // 2, (top_left[1] + bottom_right[1]) // 2
                self.target_img.point = center[0] + self.target_img.adj[0], center[1] + self.target_img.adj[1]

        # 3. 이미지 TK로 변환
        screen_tk = convert_screen(screen)

        # 4. 이미지 라벨 업데이트
        update_img_label(screen_tk)

        # 5. 루프 수행
        self.after(30, self.img_routine)

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

    def init_work(self):
        self.is_wifi_connected = self.check_wifi()

        # 와이파이 접속 여부 확인: 5초
        for wifi_wait_second in range(0, 5):
            if self.is_wifi_connected:
                break
            else:
                time.sleep(1)

        # 5초 이후 접속 확인 안되었을 경우 와이파이 구동
        if not self.is_wifi_connected:
            self.logging("사내망 wifi 연결 프로그램 구동")
            wifi_manager = ThirdPartyOperator(r"C:\Program Files\Unetsystem\AnyClick\AnyMgm.exe")
            wifi_manager.run()

            # 와이파이 구동 되었는지 확인 위한 이미지 타겟 설정
            self.load_img("wifi_manager", (-65, -115))
            self.logging("wifi_manager 검색 시작")
            
        # 구동 대기 및 이미지 찾기를 위한 루프 -> 딴데서 돌아야함. 얘들도 멈춘다.
        while True:
            
            # 이미지를 찾았다면 좌표 설정이 되어있음, 좌표 가져오고 이미지 언로드함
            if self.target_img.point:
                self.logging("wifi_manager 확인 완료")
                current_target_point = self.target_img.point
                self.unload_img()
                break

        # 이동명령 수행 루프
                


if __name__ == '__main__':
    jarvis = TkWrapper()
    jarvis.mainloop()
