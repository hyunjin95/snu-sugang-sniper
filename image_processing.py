import cv2
import numpy as np
from io import BytesIO


# 수강신청 확인문자 이미지를 읽어서 해당 숫자 리턴.
def get_number_from_image(driver):
    # 현재 화면 캡쳐
    screenshot = BytesIO(driver.get_screenshot_as_png())

    # 이미지의 위치, 크기 가져와서 스크린샷에서 이미지 crop
    location, size = _get_image_location_and_size(driver)
    img = _crop_screenshot(screenshot, location, size)
    print("Got image!")

    return "34"


# 이미지 위치와 크기 리턴.
def _get_image_location_and_size(driver):
    element = driver.find_element_by_class_name("num")
    location = element.location
    size = element.size
    return (location, size)


# 수강신청 확인문자를 이미지로 변환 후 메모리에 저장
def _crop_screenshot(screenshot, location, size):
    img = cv2.imdecode(np.frombuffer(screenshot.read(), np.uint8), 1)

    left = location["x"]
    top = location["y"]
    right = location["x"] + size["width"]
    bottom = location["y"] + size["height"]

    return _preprocess_image(img[top:bottom, left:right])
    

# 이미지 전처리
def _preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    upscale = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    return upscale



