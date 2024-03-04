from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from PIL import Image, ImageFilter, ImageOps
from scipy.ndimage import gaussian_filter
import numpy as np
import pytesseract
from scipy import ndimage
from io import BytesIO
import cv2
from twocaptcha import TwoCaptcha
import time
from base64 import b64encode
import io


def get_screenshot(driver, id) -> bytes:
    image = driver.find_element(By.ID, "ctl00_MainContent_imgSecNum")
    png = image.screenshot_as_png
    im = Image.open(BytesIO(png))
    width, height = im.size
    new_width = width//3
    im = im.crop((new_width, 0, new_width * 2, height))
    img_byte_arr = io.BytesIO()
    # image.save expects a file-like as a argument
    im.save(img_byte_arr, format='png')
    # Turn the BytesIO object back into a bytes object
    img_byte_arr = img_byte_arr.getvalue()
    return b64encode(img_byte_arr).decode('utf-8')


def solve_captcha(b64image) -> str:
    solver = TwoCaptcha("47c6ec2a004a531edab27bf6068d3516")

    result = solver.normal(b64image, numeric=1)
    return result["code"]

URL = "https://belgrad.kdmid.ru/queue/orderinfo.aspx?id=75490&cd=d645e055&ems=97BF4526"

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
options.add_argument("--kiosk")

driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.get(URL)
screenshot = get_screenshot(driver, "ctl00_MainContent_imgSecNum")
captcha = solve_captcha(screenshot)

captcha_input = driver.find_element(By.ID, "ctl00_MainContent_txtCode")
captcha_input.send_keys(captcha)
captcha_input.send_keys(Keys.ENTER)
wait = WebDriverWait(driver, 30)

button_input = wait.until(
    EC.visibility_of_all_elements_located((
        By.ID,
        "ctl00_MainContent_ButtonB"
    ))
)
print(button_input)
button_input[0].send_keys(Keys.ENTER)

text = "Извините, но в настоящий момент на интересующее Вас консульское действие в системе предварительной записи нет свободного времени."

if text in driver.page_source:
    print("NOT FOUND:(")