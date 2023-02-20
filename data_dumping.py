import os
import cv2
import pickle


def pickle_img(png_img_name):
    img = cv2.imread(r"D:\jarvis\{}.png".format(png_img_name), cv2.IMREAD_COLOR)
    with open(r"D:\jarvis\pickles\{}.imgData".format(png_img_name), "wb") as file:
        pickle.dump(img, file)


def check_pickle(imgData_name):
    with open(r"D:\jarvis\pickles\{}.imgData".format(imgData_name), 'rb') as f:
        data = pickle.load(f)
    cv2.imshow("current", data)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # pickle_img("wifi_manager")
    check_pickle("wifi_manager")
