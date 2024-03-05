from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from PIL import Image
from io import BytesIO
from twocaptcha import TwoCaptcha
from base64 import b64encode
import io


def get_screenshot(driver, id) -> bytes:
    image = driver.find_element(By.ID, "ctl00_MainContent_imgSecNum")
    png = image.screenshot_as_png
    im = Image.open(BytesIO(png))
    img_byte_arr = io.BytesIO()
    # image.save expects a file-like as a argument
    im.save(img_byte_arr, format='png')
    # Turn the BytesIO object back into a bytes object
    img_byte_arr = img_byte_arr.getvalue()
    return b64encode(img_byte_arr).decode('utf-8')


def solve_captcha(b64image) -> str:
    solver = TwoCaptcha("47c6ec2a004a531edab27bf6068d3516")

    result = solver.normal(b64image, numeric=1)
    print(result)
    return result["code"]

URL = "https://brussels.kdmid.ru/queue/orderinfo.aspx?id=65210&cd=063551bd&ems=11CB4602"

options = webdriver.ChromeOptions()
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.get(URL)
screenshot = get_screenshot(driver, "ctl00_MainContent_imgSecNum")
captcha = solve_captcha(screenshot)

captcha_input = driver.find_element(By.ID, "ctl00_MainContent_txtCode")
captcha_input.send_keys(captcha)
captcha_input.send_keys(Keys.ENTER)
wait = WebDriverWait(driver, 30)
png = driver.save_screenshot("wow.png")
button_input = wait.until(
    EC.visibility_of_all_elements_located((
        By.ID,
        "ctl00_MainContent_ButtonB"
    ))
)
button_input[0].send_keys(Keys.ENTER)

text = "в настоящий момент на интересующее Вас консульское действие"

print(driver.page_source)
if text in driver.page_source:
    print("NOT FOUND:(")
