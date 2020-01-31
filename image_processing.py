# 수강신청 확인문자 이미지 저장
def get_image(driver):
    image = driver.find_element_by_id("imageText")
    location = image.location
    size = {'width': 52, 'height': 26}
    screenshot = BytesIO(driver.get_screenshot_as_png())
    
    image = cv2.imdecode(np.frombuffer(screenshot.read(), np.uint8), 1)

    left = location["x"]
    top = location["y"]
    right = location["x"] + size["width"]
    bottom = location["y"] + size["height"]

    captcha = optimize_image(image[top:bottom, left:right])
    custom_oem_psm_config = r'--oem 3 --psm 8'
    cv2.imshow("catpcha", captcha)
    cv2.waitKey(0)
    # im.save(str(CURRENT_DIRECTORY / "image.png"), dpi=(52, 26)) # saves new cropped image


def optimize_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    upscale = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    return upscale


def get_num_from_image():
    pass