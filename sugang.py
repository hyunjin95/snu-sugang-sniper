from pathlib import Path
from re import search
from time import sleep
from winsound import Beep
from io import BytesIO

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import cv2
import numpy as np

from image_processing import get_image



CURRENT_DIRECTORY = Path(__file__).parent.absolute()


# # 빈 자리 날 때까지 무한루프 돌면서 체크
# def snipe_vacancy(driver):
#     try:
#         login(driver)
#         # 로그인 후 로딩이 될 때까지 기다려준다.
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "log_ok")))
#         row_num = -1

#         while True:
#             row_num = rownum_vacancy_in_interested_lectures(driver)
#             if row_num >= 0:
#                 break
#             sleep(1) 

#         # 빈 강의가 있으면 비프음으로 알린 후 수강 신청
#         Beep(2000, 5000)
#         lectures = driver.find_elements_by_css_selector("tr > td:nth-child(1) > input[type=checkbox]:nth-child(1)")
#         lectures[row_num].click()    
#         register(driver)
#     except BaseException as e:
#         # 에러가 났을 경우 함수를 다시 실행해봄. 비프로 에러 알림.
#         Beep(5000, 3000)
#         print(e.message)
#         snipe_vacancy(driver)    


def snipe_vacancy(driver):
    try:
        login(driver)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "log_ok")))
        row_num = -1
        # row_num = rownum_vacancy_in_interested_lectures(driver)  
        lectures = driver.find_elements_by_css_selector("tr > td:nth-child(1) > input[type=checkbox]:nth-child(1)")
        lectures[row_num].click()    
        register(driver)
        Beep(2000, 5000)
    except BaseException as e:
        # 에러가 났을 경우 함수를 다시 실행해봄. 비프로 에러 알림.
        print(e)
        Beep(5000, 3000)
        snipe_vacancy(driver)


def login(driver):
    driver.get("http://sugang.snu.ac.kr")
    driver.implicitly_wait(10)
    # iframe을 사용하기 때문에 switch 해준다.
    driver.switch_to.frame("main")

    driver.find_element_by_id("j_username").send_keys("2013-11431")
    # 패스워드는 클릭해야 정보를 입력할 수 있게 되어 있어서 두 단계로 나눔.
    driver.find_element_by_id("t_password").click()
    driver.find_element_by_id("v_password").send_keys("hyunjin0119")

    # 로그인
    driver.find_element_by_xpath("//*[@id='CO010']/div/div/p[3]/a").click()
    

# 관심 강좌 목록 체크, 빈 강좌 있으면 해당 행 번호 리턴
def rownum_vacancy_in_interested_lectures(driver):
    # 관심강좌 메뉴 클릭 (새로고침은 막아 놓음)
    driver.find_element_by_xpath("//*[@id='submenu01']/li[3]/a").click()
    # 페이지가 로딩될 때까지 기다리기.
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tbl_basic")))

    # save_image(driver)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # 총 정원
    # number_maximum = [int(search(".*\(", td.text.strip()).group(0)[:-2]) for td in soup.select("tr > td:nth-child(14)")]
    # 재학생 정원
    number_maximum_not_junior = [int(search("\(.*\)", td.text.strip()).group(0)[1:-1]) for td in soup.select("tr > td:nth-child(14)")]
    # 등록 인원
    number_registered_people = [int(td.text.strip()) for td in soup.select("tr > td:nth-child(15)")]

    # 관심강좌 목록 살펴보기
    for index, tuple in enumerate(zip(number_maximum_not_junior, number_registered_people)):
        maximum, registered = tuple
        # 해당하는 강좌의 row 번호를 리턴.
        if registered < maximum:
            return index
    return -1


def register(driver):
    captcha_num = get_num_from_image()
    driver.find_element_by_id("inputTextView").send_keys("94")
    driver.find_element_by_xpath("//*[@id='content']/div/div[2]/div[2]/div[2]/a").click()


if __name__ == "__main__":
    # Path 얻기
    webdriver_path = str(CURRENT_DIRECTORY / "chromedriver.exe")

    # 드라이버 로딩
    driver = webdriver.Chrome(webdriver_path)
    driver.implicitly_wait(3)
    
    # 빈 자리 탐색하고 있으면 수강
    snipe_vacancy(driver)
