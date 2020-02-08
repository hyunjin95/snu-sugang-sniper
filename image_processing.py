import math
from io import BytesIO

import cv2
import numpy as np
from scipy import ndimage

from mnist import load_model



# 수강신청 확인문자 이미지를 읽어서 해당 숫자 리턴.
def get_number_from_image(driver):
    # 현재 화면 캡쳐
    screenshot = BytesIO(driver.get_screenshot_as_png())

    # 이미지의 위치, 크기 가져와서 스크린샷에서 이미지 crop
    location, size = _get_image_location_and_size(driver)
    img = _crop_screenshot(screenshot, location, size)
    preprocessed_img = _preprocess_image(img)

    # 자릿수별로 이미지 나눈 후 한 자리씩 예측한 후 결과값 리턴
    tens, ones = _divide_image(img, preprocessed_img)
    return _predict_double_digits(tens, ones)


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
def _preprocess_image(img):
    # 그레이스케일로 변환
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 이진화 처리
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    # Contour를 위해 흑백 반전
    gray_inverse = cv2.bitwise_not(gray)
    return gray_inverse


# 2자릿수 숫자의 이미지를 한 자릿수 숫자 2개의 이미지로 분리
def _divide_image(img, preprocessed_img):
    # findContours 함수를 이용해서 숫자 범위들 찾기.
    contours, hierachy = cv2.findContours(preprocessed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    img_locations = _get_img_locations(contours)

    # 좌표값들 변환
    loc_tens, loc_ones = img_locations[0], img_locations[1]
    tens_x, tens_y, tens_w, tens_h = loc_tens.get("x"), loc_tens.get("y"), loc_tens.get("w"), loc_tens.get("h")
    ones_x, ones_y, ones_w, ones_h = loc_ones.get("x"), loc_ones.get("y"), loc_ones.get("w"), loc_ones.get("h")

    # 이미지 나누기
    tens = preprocessed_img[tens_y:tens_y+tens_h, tens_x:tens_x+tens_w]
    ones = preprocessed_img[ones_y:ones_y+ones_h, ones_x:ones_x+ones_w]

    # MNIST 이미지들과 동일하게 28x28 이미지로 변환.
    resized_tens = cv2.resize(tens, (28, 28), interpolation=cv2.INTER_CUBIC)
    resized_ones = cv2.resize(ones, (28, 28), interpolation=cv2.INTER_CUBIC)
    
    # 예측 정확도를 높이기 위해 패딩 적용해서 숫자 가운데 위치
    padded_tens = _add_padings(tens)
    padded_ones = _add_padings(ones)

    return (padded_tens, padded_ones)


# 이미지들의 좌표 얻기
def _get_img_locations(contours):
    image_locations = []

    # cnt 순서가 왼쪽->오른쪽 순서로 항상 보장이 되지 않기 때문에 x 좌표값을 체크해서 순서 정해줌.
    for cnt in contours:
        # 찾은 Contour들의 직사각형 그리기
        x, y, w, h = cv2.boundingRect(cnt)
        location = {"x": x, "y": y, "w": w, "h": h}
        # 너무 작은 값은 무시하도록 높이가 8px 이상일 때만 저장.
        if h >= 8:
            if not image_locations or image_locations[0].get("x") < x:
                image_locations.append(location)
            else:
                image_locations.insert(0, location)
    
    return image_locations


# MNIST 이미지 형식에 맞게 이미지에 패딩 추가
def _add_padings(img):
    rows, cols = img.shape
    
    if rows > cols:
        factor = 20.0 / rows
        rows, cols = 20, int(round(cols * factor))
    else:
        factor = 20.0 / cols
        rows, cols = int(round(rows * factor)), 20
    
    img = cv2.resize(img, (cols, rows))
    rows_padding = (int(math.ceil((28 - rows) / 2.0)), int(math.floor((28 - rows) / 2.0)))
    cols_padding = (int(math.ceil((28 - cols) / 2.0)), int(math.floor((28 - cols) / 2.0)))
    img = np.lib.pad(img, (rows_padding, cols_padding), "constant")

    shift_x, shift_y = _get_best_shift(img)
    return _shift(img, shift_x, shift_y)


# 이미지가 이동할 값 리턴
def _get_best_shift(img):
    cy, cx = ndimage.measurements.center_of_mass(img)
    rows, cols = img.shape

    shift_x = np.round(cols/2.0 - cx).astype(int)
    shift_y = np.round(rows/2.0 - cy).astype(int)

    return (shift_x, shift_y)


# 이미지 이동
def _shift(img, shift_x, shift_y):
    rows, cols = img.shape
    M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    return cv2.warpAffine(img, M, (cols, rows))


# 숫자 이미지 2개 예측 후 2자릿수 스트링으로 리턴.
def _predict_double_digits(tens, ones):
    flatted_tens = tens.reshape(-1, 28*28) / 255.0
    flatted_ones = ones.reshape(-1, 28*28) / 255.0

    # 모델 로드 후 예측
    model = load_model()
    tens_prediction, ones_prediction = np.argmax(model.predict(flatted_tens)), np.argmax(model.predict(flatted_ones))

    prediction = str(tens_prediction) + str(ones_prediction)
    return prediction
