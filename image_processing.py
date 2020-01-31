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
    processed_img, processed_img_inverse = _preprocess_images(img)
    # 자릿수별로 이미지 나눈 후 한 자리씩 예측한 후 결과값 리턴
    tens, ones = divide_image(img, processed_img, processed_img_inverse)
    # return predict(tens, ones)


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

    return img[top:bottom, left:right]
    

# 이미지 전처리
def _preprocess_images(img):
    # 그레이스케일로 변환
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 이진화 처리
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    # Contour를 위해 흑백 반전
    gray_inverse = cv2.bitwise_not(gray)
    # 업스케일링
    # upscale = cv2.resize(gray_inverse, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    return (gray, gray_inverse)


# 2자릿수 숫자의 이미지를 한 자릿수 숫자 2개의 이미지로 분리
def divide_image(img, processed_img, processed_img_inverse):
    contours, hierachy = cv2.findContours(processed_img_inverse, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return_img_locations = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        location = {"x": x, "y": y, "w": w, "h": h}
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)
        if h >= 8:
            if not return_img_locations or return_img_locations[0].get("x") < x:
                return_img_locations.append(location)
            else:
                return_img_locations.insert(0, location)

    loc_tens, loc_ones = return_img_locations[0], return_img_locations[1]
    tens_x, tens_y, tens_w, tens_h = loc_tens.get("x"), loc_tens.get("y"), loc_tens.get("w"), loc_tens.get("h")
    ones_x, ones_y, ones_w, ones_h = loc_ones.get("x"), loc_ones.get("y"), loc_ones.get("w"), loc_ones.get("h")

    tens = processed_img[tens_y:tens_y+tens_h, tens_x:tens_x+tens_w]
    ones = processed_img[ones_y:ones_y+ones_h, ones_x:ones_x+ones_w]

    cv2.imshow("img", img)
    cv2.waitKey(0)
    cv2.imshow("img", tens)
    cv2.waitKey(0)
    cv2.imshow("img", ones)
    cv2.waitKey(0)


# 이미지 2개 예측
def predict(tens, ones):
    return 00
