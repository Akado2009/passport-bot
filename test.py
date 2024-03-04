from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from PIL import Image, ImageFilter, ImageOps
from scipy.ndimage import gaussian_filter
import numpy as np
import pytesseract
from scipy import ndimage
from io import BytesIO
import cv2
from twocaptcha import TwoCaptcha
import time

SCREEN_PATH = "screenshot.png"


captcha_client = TwoCaptcha("47c6ec2a004a531edab27bf6068d3516")

def solve_2captcha() -> str:
    # resize iamg
    solver = TwoCaptcha("47c6ec2a004a531edab27bf6068d3516")

    result = solver.normal(file=SCREEN_PATH, numeric=1)
   
    print(result)
    return ""

def rotate_image(image, angle):
  image_center = tuple(np.array(image.shape[1::-1]) / 2)
  rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
  result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
  return result

def save_image(driver: webdriver.Chrome, id: str) -> None:
    image = driver.find_element(By.ID, "ctl00_MainContent_imgSecNum")
    location = image.location
    size = image.size
    # png = driver.get_screenshot_as_png()
    png = image.screenshot_as_png

    im = Image.open(BytesIO(png))
    im.save(SCREEN_PATH) 

def solve_captcha() -> str:
    img = cv2.imread(SCREEN_PATH, cv2.IMREAD_GRAYSCALE)
    # img = rotate_image(img, 30)
    # crop by third
    width = img.shape[1]
    height = img.shape[0]
    new_width = width//3
    img = img[0: height, new_width:2 * new_width]
    (h, w) = img.shape[:2]
    gry = cv2.resize(img, (w * 2, h * 2))
    cls = cv2.morphologyEx(gry, cv2.MORPH_CLOSE, None)
    cv2.imwrite("close.png", cls)
    thr = cv2.threshold(cls, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    thr = cv2.resize(thr, (0,0), fx=3, fy=1.5) 

    cv2.imwrite("thr.png", thr)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    # opening the image
    opening = 255 - cv2.morphologyEx(thr, cv2.MORPH_OPEN, kernel, iterations=1)
    opening = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
    contours, hierarchy = cv2.findContours(opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    filled_circles_contours = list()
    parent_contours = [contours[idx] for idx, val in enumerate(hierarchy[0]) if val[3] == -1]
    mask = np.zeros(opening.shape[:2], dtype=opening.dtype)
    for contour in parent_contours:

        contour_mask = np.zeros(opening.shape).astype("uint8")
        cv2.drawContours(contour_mask, [contour], -1, 1, thickness=-1)
        cmask = cv2.findNonZero(contour_mask)
        if cmask is not None:
            white_len_mask = len(cv2.findNonZero(contour_mask))
            white_len_thresholded = len(cv2.findNonZero(contour_mask * opening))
            white_ratio = float(white_len_thresholded) / white_len_mask

            if white_ratio < 0.99:
                filled_circles_contours.append(contour)

    cv2.drawContours(mask, filled_circles_contours, -1, (255), -1)
    # cv2.drawContours(opening, filled_circles_contours, -1, (100, 100, 100), thickness=10)
    cv2.imwrite("final.png", opening)
    opening = cv2.bitwise_and(opening, opening, mask=mask)
    cv2.imwrite("final.png", opening)
    # angle = -15
    # image_center = tuple(np.array(opening.shape[1::-1]) / 2)
    # rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    # opening = cv2.warpAffine(opening, rot_mat, opening.shape[1::-1], flags=cv2.INTER_LINEAR)
    # opening = opening[130:290, 300:800]
    for i in range(3, 14):
        txt = pytesseract.image_to_string(
            opening,
            config=f'--psm {i} --oem 3 -c tessedit_char_whitelist=[0123456789]'
        )
        possible_lines = txt.splitlines()
        print(i, possible_lines)
# def solve_captcha() -> str:
#     th1 = 140
#     th2 = 140
#     sig = 1.3
#     original = Image.open(SCREEN_PATH)
#     black_and_white = original.convert("L")
#     black_and_white.save("black_and_white.png")
#     first_threshold = black_and_white.point(lambda p: p > th1 and 255)
#     first_threshold.save("first_threshold.png")
#     blur = np.array(first_threshold)
#     blurred = gaussian_filter(blur, sigma=sig)
#     blurred = Image.fromarray(blurred)
#     blurred.save("blurred.png")
#     final = blurred.point(lambda p: p > th2 and 255)
#     final = final.filter(ImageFilter.EDGE_ENHANCE_MORE)
#     final = final.filter(ImageFilter.SHARPEN)
#     final = ImageOps.autocontrast(final)
#     final.save("final.png")
#     # final = final.filter(ImageFilter.FIND_EDGES)
#     kernel = np.ones((7, 7),np.uint8)
#     final = cv2.imread('final.png',0)
#     closing = cv2.morphologyEx(final, cv2.MORPH_OPEN, kernel)
#     number = pytesseract.image_to_string(
#         Image.open(SCREEN_PATH),
#         lang='eng',
#         config='--psm 10 --oem 3 -c tessedit_char_whitelist=[0123456789]'
#     ).strip()
#     cv2.imwrite('closing.png', closing) 


#     print("RESULT OF CAPTCHA:")
#     print(number)
#     print("===================")
#     return ""

# URL = "https://belgrad.kdmid.ru/queue/orderinfo.aspx?id=75490&cd=d645e055&ems=97BF4526"

# options = webdriver.ChromeOptions()
# # options.add_experimental_option("detach", True)
# options.add_argument("--kiosk")

# driver = webdriver.Chrome(options=options)
# driver.maximize_window()
# driver.get(URL)
# save_image(driver, "ctl00_MainContent_imgSecNum")
# solve_captcha()
solve_2captcha()