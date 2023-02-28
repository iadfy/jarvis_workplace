from tkinter import *
from img import *

import socket
import subprocess
import os

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


class AutomationOperator(threading.Thread):
    def __init__(self, root):
        threading.Thread.__init__(self)
        self.root = root
        self.prohibit_next_switch = False

    def run(self):
        while True:
            # 2초마다 작업 확인
            time.sleep(2)

            # 1. 대기 작업 없거나 후속작업 차단 스위치가 켜져있으면 패스
            if len(self.root.operation_q) == 0 or self.prohibit_next_switch:
                continue

            # 2. 스위치가 꺼져있고, 대기 작업 있을 경우, 파싱해서 가져온 다음 스위치 켬
            direction, parameter = self.root.operation_q.popleft()  # q: (작업, (파라미터))
            self.prohibit_next_switch = True

            # 3. 현재 작업이 종료되었는지 계속 확인하는 루프 생성 -> 종료시 break
            while True:

                # 3-1. 현재 작업이 마우스 이동인 경우
                if direction == "moveTo":
                    # 3-1-1. 타겟 좌표 = 현재좌표 이면 스위치를 끄고 break
                    if (at.position().x, at.position().y) == parameter:
                        self.root.logging("이동작업 수행 완료 {}".format(at.position()))
                        self.prohibit_next_switch = False
                        break

                    # 3-1-2. 아니면 계속 마우스 이동
                    else:
                        at.moveTo(parameter)

                # 3-2. 클릭인 경우
                if direction == "click":
                    at.click()
                    self.root.logging("클릭 수행 완료 {}".format(at.position()))
                    self.prohibit_next_switch = False
                    break

                # 3-3. 더블클릭인 경우
                if direction == "doubleClick":
                    at.doubleClick()
                    self.root.logging("더블클릭 수행 완료 {}".format(at.position()))
                    self.prohibit_next_switch = False
                    break


class TkWrapper(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.is_wifi_connected: bool = False

        self.operation_q = deque([])

        self.target_img = None, None

        # region 자동화 쓰레드
        self.operator = AutomationOperator(self)
        self.operator.start()
        # endregion

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

        self.operation_wait = Listbox(self, height=30, width=50)
        self.operation_wait.grid(row=1, column=0)

        # self.target_label = Label(self, relief="solid")
        # self.target_label.grid(row=1, column=0)
        # self.current_label = Label(self, relief="solid")
        # self.current_label.grid(row=1, column=1)
        # endregion

    def update_img_label(self, img):
        # img: ImgTk
        self.img_label.config(image=img)
        self.img_label.image = img

    def img_routine(self):

        current_point = (None, None)

        # 1. 스크린 캡쳐
        screen_capture: cv2 = bring_screen()

        # 2. 타겟 이미지가 존재하면 타겟 이미지를 찾는다.
        if self.target_img[0] is not None:
            screen_capture, current_point = find_target(self.target_img[0], screen_capture)

            # 2-1. 타겟 이미지를 찾았으면,
            if current_point[0] is not None and current_point[1] is not None:
                self.logging("타겟 이미지 발견")

                # 2-1-1. 좌표 세부조정을 설정한다.
                if self.target_img[1] == "wifi_manager":
                    current_point = (current_point[0] - 65, current_point[1] - 115)

                # 2-1-2. 타겟 이미지를 지운다.
                self.target_img = None, None  # --> 그러면 find_target 차단됨

        # 3. current point가 존재하고, 각 좌표가 None이 아니면 이동 명령을 큐에 전달
        if current_point and current_point[0] is not None and current_point[1] is not None:
            self.operation_q.append(("moveTo", current_point))
            self.logging("작업 추가: {}으로 이동".format(current_point))

        # 4. 이미지 TK로 변환
        screen_capture = convert_screen(screen_capture)

        # 5. 이미지 라벨 업데이트
        self.update_img_label(screen_capture)

        # 6. 현재 작업을 queue에 표시
        self.operation_wait.delete(0, END)

        for operation in self.operation_q:
            self.operation_wait.insert(END, "{}: {}".format(operation[0], operation[1]))

        self.after(100, self.img_routine)

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

    def init_work(self):
        self.is_wifi_connected = self.check_wifi()
        if self.is_wifi_connected:  # not
            self.logging("사내망 wifi 연결 프로그램 구동")
            wifi_manager = ThirdPartyOperator(r"C:\Program Files\Unetsystem\AnyClick\AnyMgm.exe")
            wifi_manager.run()
            self.target_img = set_target_img("wifi_manager")
            self.logging("타겟 이미지 설정: 사내망 wifi 연결 프로그램")

            self.operation_q.append(("doubleClick", (None, None)))
            self.logging("더블클릭 작업 대기열 추가 완료")


if __name__ == '__main__':
    jarvis = TkWrapper()
    jarvis.mainloop()
