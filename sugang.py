# 파이썬 자체 내장 라이브러리
from re import search
from time import sleep
from winsound import MessageBeep
from datetime import datetime
from traceback import print_exc

# 따로 설치해야 하는 라이브러리
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 프로젝트 모듈
from path import static_directory_path, webdriver_path, tf_model_path
from image_processing import get_number_from_image
from mnist import save_model, SingletonModel



# 로그인에 사용되는 아이디와 비밀번호
USER_ID = "YOUR_ID"
USER_PW = "YOUR_PW"
# 강좌에 신입생 포함 유무. 1학기 재학생 수강신청 기간에만 True로 설정.
EXCLUDE_JUNIORS = True
# 새로고침 주기.
REFRESH_INTERVAL_IN_SECONDS = 0.5
# 브라우저 로딩에 기다려줄 최대 시간
WAIT_LIMIT_IN_SECONDS = 10


# 드라이버 불러오기
def load_driver():
    options = webdriver.ChromeOptions()
    # 해상도와 디스플레이 배율에 상관 없이 일관된 화면이 표시되도록 설정.
    options.add_argument("window-size=1920x1080")
    options.add_argument("force-device-scale-factor=1")
    driver = webdriver.Chrome(str(webdriver_path()), options=options)
    driver.implicitly_wait(WAIT_LIMIT_IN_SECONDS)
    return driver


# 관심 강좌에서 자리가 비는 강의를 찾아서 수강 신청해준다.
def snipe_vacancy():
    driver = load_driver()
    print(get_current_time(), "-", "프로그램 시작")
    try:
        # 수강신청 사이트는 쿠키가 있으면 접속이 안 되기 때문에 모두 지워줌.
        driver.delete_all_cookies()
        login(driver)
        # 로그인 후 로딩이 될 때까지 기다려준다.
        WebDriverWait(driver, WAIT_LIMIT_IN_SECONDS).until(EC.presence_of_element_located((By.CLASS_NAME, "log_ok")))
        # 빈 강좌를 찾는다.
        row_num = find_vacancy(driver)

        # 신청할 강의 클릭
        lectures = driver.find_elements_by_css_selector("tr > td:nth-child(1) > input[type=checkbox]:nth-child(1)")
        lectures[row_num].click()
        lecture_name = driver.find_elements_by_css_selector("tr > td:nth-child(8) > a")[row_num].text

        captcha_num = get_number_from_image(driver)        
        register(driver, captcha_num)
    except BaseException:
        print_exc()
        driver.quit()
        snipe_vacancy()


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
    

# 빈 강좌를 찾을 때까지 실행.
def find_vacancy(driver):
    row_num = -1
    while row_num == -1:
        row_num = rownum_in_interested_lectures(driver)
        sleep(REFRESH_INTERVAL_IN_SECONDS)
    return row_num


# 관심 강좌 목록 체크, 빈 강좌 있으면 해당 행 번호 리턴
def rownum_in_interested_lectures(driver):
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
def register(driver, captcha_num, lecture_name):
    msg = ""
    # 빈 강의가 있으면 비프음으로 알린 후 수강 신청.
    MessageBeep()
    try:
        driver.find_element_by_id("inputTextView").send_keys(captcha_num)
        driver.find_element_by_xpath("//*[@id='content']/div/div[2]/div[2]/div[2]/a").click()
        
        WebDriverWait(driver, WAIT_LIMIT_IN_SECONDS).until(EC.alert_is_present())
        alert = driver.switch_to.alert

        msg = alert.text
        alert.accept()
    except TimeoutException:
        print("알람이 떠야하는데 안 뜸.")
    finally:
        # 수강신청 성공하면 그만 돌려도 되니까 드라이버 종료.
        if "수강신청되었습니다" in msg:
            print_msg(True, lecture_name, msg)
            driver.quit()
        else:
            # 다른 메시지가 출력되면 신청 실패. 다시 처음으로 돌아가기.
            print_msg(False, lecture_name, msg)
            snipe_vacancy(driver)


# 수강신청시 로그 메시지 출력
def print_msg(is_success, lecture_name, msg):
    str_is_success = "- 수강신청 성공!!!!!!!!!!!!!!!!! -" if is_success else "- 수강신청 실패... -"
    current_time = get_current_time()

    s = " ".join([current_time, lecture_name, str_is_success, msg])
    print(s)


# 현재 시간 스트링
def get_current_time():
    now = datetime.now()
    return now.strftime("[%H:%M:%S]")


if __name__ == "__main__":
    # 모델이 경로에 없을 경우 생성해준다.
    if not tf_model_path().exists():
        save_model()

    # 인스턴스 초기 생성. 첫 생성을 시작 때 해서 Register에 걸리는 시간을 줄인다.
    SingletonModel.instance()
    
    # 관심강좌 중 빈 자리 탐색하고, 있으면 수강 신청.
    # 모델을 반복적으로 생성하지 않기 위해 메인에서 생성 후 함수 인자로 넘겨준다.
    snipe_vacancy()
