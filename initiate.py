import pyautogui as at
import subprocess
import numpy as np
import cv2
import time
import pickle
from PIL import ImageGrab
from win32gui import GetWindowText, GetForegroundWindow
from tkinter import *


def find_app(app_name: str):
    print(GetWindowText())
#
#
# def run_edge():
#     subprocess.run(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
#
#
# def take_screen():
#     screenshot = ImageGrab.grab((0, 0, 1920, 1080))
#     screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
#     return screenshot

#
# def find_target(target_pic_cv, threshold=0.95):
#     h, w, d = target_pic_cv.shape
#
#     current_screen = take_screen()
#     result = cv2.matchTemplate(current_screen, target_pic_cv, cv2.TM_CCOEFF_NORMED)
#     # cv2.imshow("target", target_pic_cv)
#     # cv2.waitKey(0)
#     # cv2.destroyAllWindows()
#     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
#     if max_val > threshold:
#         x, y = max_loc
#         bottom_right = (x + w, y + h)
#         cv2.rectangle(current_screen, (x, y), bottom_right, (0, 0, 255), 5)
#
#         # cv2.imshow("current", current_screen)
#         # cv2.waitKey(0)
#         # cv2.destroyAllWindows()
#         center = (x + w // 2, y + h // 2)
#         return center
#     else:
#         return None

#
# def take_pickle(target_pickle_path: str):
#     with open(target_pickle_path, 'rb') as f:
#         data = pickle.load(f)
#     return data


if __name__ == '__main__':
    pw_wifi_img = take_pickle(r"D:\jarvis\pw_wifi.imgData")
    pw_img = take_pickle(r"D:\jarvis\pw.imgData")
    pw_activated = take_pickle(r"D:\jarvis\pw_activated.imgData")
    login_img = take_pickle(r"D:\jarvis\login.imgData")

    while True:
        is_wifi_connected = find_target(pw_wifi_img)
        if is_wifi_connected:
            break
        time.sleep(0.5)

    if is_wifi_connected:
        at.click(is_wifi_connected)
        time.sleep(0.05)
        at.write("thsals2@", interval=0.1)
        at.press("enter")

    run_edge()

    while True:
        is_knox_opened = find_target(pw_img)
        is_knox_opened_activated = find_target(pw_activated)
        if is_knox_opened or is_knox_opened_activated:
            break
        time.sleep(0.5)

    if is_knox_opened:
        at.click(is_knox_opened)
        time.sleep(0.05)
        at.write("thsals2@", interval=0.1)
        at.press("enter")
