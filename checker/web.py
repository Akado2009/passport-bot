from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from io import BytesIO
from twocaptcha import TwoCaptcha
from base64 import b64encode
import io
from PIL import Image
import logging
from checker.const import (
    BUTTON_ID,
    CAPTCHA_IMG_ID,
    CAPTCHA_INPUT_ID,
    TWOCAPTCHA_TOKEN,
    NOT_FOUND_TEXT,
)

def selenium_check_slots(url: str) -> bool:
    logger = logging.getLogger(__name__)
    result = False
    try:
        driver = init_driver()
        driver.maximize_window()
        driver.get(url)
        screenshot = get_screenshot(driver, CAPTCHA_IMG_ID, url)
        captcha = solve_captcha(screenshot)
        captcha_input = driver.find_element(By.ID, CAPTCHA_INPUT_ID)
        captcha_input.send_keys(captcha)
        captcha_input.send_keys(Keys.ENTER)

        wait = WebDriverWait(driver, 30)

        button_input = wait.until(
            EC.visibility_of_all_elements_located((
                By.ID,
                BUTTON_ID,
            ))
        )
        button_input[0].send_keys(Keys.ENTER)
        result = NOT_FOUND_TEXT not in driver.page_source 
    except Exception as e:
        logger.info("ERROR WOWOWOWOW", e)
    return result        


def init_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()

    options.add_argument('--no-sandbox')
    # options.add_experimental_option("detach", True)
    options.add_argument('--headless')
    # options.add_argument("--kiosk")

    driver = webdriver.Chrome(options=options)
    return driver


def get_screenshot(driver, id, url) -> bytes:
    image = driver.find_element(By.ID, id)
    png = image.screenshot_as_png
    im = Image.open(BytesIO(png))
    if 'belgrad' in url:
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
    solver = TwoCaptcha(TWOCAPTCHA_TOKEN)

    result = solver.normal(b64image, numeric=1)
    return result["code"]

