# 파이썬 자체 내장 라이브러리들
from pathlib import Path
from re import search
from time import sleep
from winsound import MessageBeep, Beep
from traceback import format_exc

# 따로 설치해야 하는 라이브러리
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from image_processing import get_number_from_image



# 로그인에 사용되는 아이디와 비밀번호
USER_ID = '2013-11431'
USER_PW = 'hyunjin0119'
# 강좌에 신입생 포함 유무. 1학기 재학생 수강신청 기간에만 True로 설정.
EXCLUDE_JUNIORS = True
# 새로고침 주기. 기본은 1초
REFRESH_INTERVAL_IN_SECONDS = 1
# 브라우저 로딩에 기다려줄 시간
WAIT_LIMIT_IN_SECONDS = 10


# 관심 강좌에서 자리가 비는 강의를 찾아서 수강 신청해준다.
def snipe_vacancy(driver):
    try:
        login(driver)
        # 로그인 후 로딩이 될 때까지 기다려준다.
        WebDriverWait(driver, WAIT_LIMIT_IN_SECONDS).until(EC.presence_of_element_located((By.CLASS_NAME, "log_ok")))
        row_num = -1

        # 빈 자리 날 때까지 무한루프 돌면서 체크
        while True:
            row_num = rownum_vacancy_in_interested_lectures(driver)
            if row_num >= 0:
                break
            sleep(REFRESH_INTERVAL_IN_SECONDS) 

        # 신청할 강의 클릭
        lectures = driver.find_elements_by_css_selector("tr > td:nth-child(1) > input[type=checkbox]:nth-child(1)")
        lectures[row_num].click()

        # 빈 강의가 있으면 비프음으로 알린 후 수강 신청
        MessageBeep()
        captcha_num = get_number_from_image(driver)
        register(driver, captcha_num)
    except BaseException:
        print(format_exc())
        handle_error(driver)    


# 개발용 - 반복 없는 snipe_vacancy 함수
def test_snipe_vacancy_without_loop(driver):
    try:
        login(driver)
        WebDriverWait(driver, WAIT_LIMIT_IN_SECONDS).until(EC.presence_of_element_located((By.CLASS_NAME, "log_ok")))

        row_num = rownum_vacancy_in_interested_lectures(driver)
        lectures = driver.find_elements_by_css_selector("tr > td:nth-child(1) > input[type=checkbox]:nth-child(1)")
        lectures[row_num].click()

        MessageBeep()
        captcha_num = get_number_from_image(driver)
        register(driver, captcha_num)
    except BaseException:
        print(format_exc())


# 사이트에 접속 후 로그인.
def login(driver):
    driver.get("http://sugang.snu.ac.kr")
    driver.implicitly_wait(WAIT_LIMIT_IN_SECONDS)
    # 사이트가 iframe을 사용하기 때문에 switch 해준다.
    driver.switch_to.frame("main")

    driver.find_element_by_id("j_username").send_keys(USER_ID)
    # 패스워드는 클릭해야 정보를 입력할 수 있게 되어 있어서 두 단계로 나눔.
    driver.find_element_by_id("t_password").click()
    driver.find_element_by_id("v_password").send_keys(USER_PW)

    # 로그인
    driver.find_element_by_xpath("//*[@id='CO010']/div/div/p[3]/a").click()
    

# 관심 강좌 목록 체크, 빈 강좌 있으면 해당 행 번호 리턴
def rownum_vacancy_in_interested_lectures(driver):
    # 관심강좌 메뉴 클릭 (새로고침은 막아 놓음)
    driver.find_element_by_xpath("//*[@id='submenu01']/li[3]/a").click()
    # 페이지가 로딩될 때까지 기다리기.
    WebDriverWait(driver, WAIT_LIMIT_IN_SECONDS).until(EC.presence_of_element_located((By.CLASS_NAME, "tbl_basic")))

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # 수강 정원
    if EXCLUDE_JUNIORS:
        number_maximum = [int(search("\(.*\)", td.text.strip()).group(0)[1:-1]) for td in soup.select("tr > td:nth-child(14)")]
    else:
        number_maximum = [int(search(".*\(", td.text.strip()).group(0)[:-2]) for td in soup.select("tr > td:nth-child(14)")]

    # 등록 인원
    number_registered_people = [int(td.text.strip()) for td in soup.select("tr > td:nth-child(15)")]

    # 관심강좌 목록 살펴보기
    for index, tuple in enumerate(zip(number_maximum, number_registered_people)):
        maximum, registered = tuple
        # 해당하는 강좌의 row 번호를 리턴.
        if registered < maximum:
            return index
    return -1


# 수강신청 확인문자를 읽어 입력 후 수강 신청 버튼 클릭.
def register(driver, captcha_num):
    driver.find_element_by_id("inputTextView").send_keys(captcha_num)
    driver.find_element_by_xpath("//*[@id='content']/div/div[2]/div[2]/div[2]/a").click()


# 에러가 생겼을 경우, alert 확인 후 작업 다시 시작.
def handle_error(driver):
    try:
        # alert가 있을 경우 확인해줘야 함.
        WebDriverWait(driver, WAIT_LIMIT_IN_SECONDS).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
    except TimeoutException:
        pass
    finally:
        # 에러가 발생했다고 알리는 비프음.
        Beep(2500, 1000)
        # 수강신청 사이트는 쿠키가 있으면 접속이 안 되기 때문에 모두 지워줌.
        driver.delete_all_cookies()
        # 다시 snipe_vacancy 함수 실행.
        snipe_vacancy(driver)
    

if __name__ == "__main__":
    # 현재 파일이 위치한 경로 얻기
    current_directory = Path(__file__).parent.absolute()
    webdriver_path = str(current_directory / "chromedriver.exe")

    # 드라이버 로딩
    options = webdriver.ChromeOptions()
    # 해상도와 디스플레이 배율에 상관 없이 일관된 화면이 표시되도록 설정.
    options.add_argument("window-size=1920x1080")
    options.add_argument("force-device-scale-factor=1")
    driver = webdriver.Chrome(webdriver_path, options=options)
    driver.implicitly_wait(WAIT_LIMIT_IN_SECONDS)

    # 관심강좌 중 빈 자리 탐색하고, 있으면 수강 신청.
    # snipe_vacancy(driver)
    test_snipe_vacancy_without_loop(driver)
