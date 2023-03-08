import threading

from PIL import Image, ImageTk, ImageGrab
import pickle
import numpy as np
import cv2
import time


def set_target_img(img_data_name: str):
    with open(r".\pickles\{}.imgData".format(img_data_name), 'rb') as f:
        data: cv2 = pickle.load(f)
    return data


def find_target(target: cv2, background: cv2, threshold=0.95):
    h, w, d = target.shape
    result = cv2.matchTemplate(background, target, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val > threshold:
        return max_loc, (w, h)
    else:
        return None


def mark_rectangular(background_img, top_left, bottom_right):
    cv2.rectangle(background_img, top_left, bottom_right, (0, 0, 255), 5)
    return background_img


def bring_screen(start_x=0, start_y=0, width=1920, height=1080) -> cv2:
    screenshot = ImageGrab.grab((start_x, start_y, width, height))
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)


def convert_screen(screen: cv2) -> ImageTk:
    screen = cv2.resize(screen, (640, 480))
    img = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    return ImageTk.PhotoImage(image=img)
