# 파이썬 자체 내장 라이브러리들
from re import search
from time import sleep
from winsound import MessageBeep

# 따로 설치해야 하는 라이브러리
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException

# 프로젝트 모듈
from path import static_directory_path, webdriver_path, tf_model_path
from image_processing import get_number_from_image
from mnist import save_model, SingletonModel



# 로그인에 사용되는 아이디와 비밀번호
USER_ID = "YOUR_ID"
USER_PW = "YOUR_PW"
# 강좌에 신입생 포함 유무. 1학기 재학생 수강신청 기간에만 True로 설정.
EXCLUDE_JUNIORS = True
# 새로고침 주기. 기본은 1초
REFRESH_INTERVAL_IN_SECONDS = 1
# 브라우저 로딩에 기다려줄 시간
WAIT_LIMIT_IN_SECONDS = 10


# 관심 강좌에서 자리가 비는 강의를 찾아서 수강 신청해준다.
def snipe_vacancy(driver):
    try:
        # 수강신청 사이트는 쿠키가 있으면 접속이 안 되기 때문에 모두 지워줌.
        driver.delete_all_cookies()
        login(driver)
        # 로그인 후 로딩이 될 때까지 기다려준다.
        WebDriverWait(driver, WAIT_LIMIT_IN_SECONDS).until(EC.presence_of_element_located((By.CLASS_NAME, "log_ok")))
        row_num = -1

        # 빈 자리 날 때까지 무한루프 돌면서 확인
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
    except NoSuchWindowException:
        # 윈도우가 없을 경우 크롬이 종료되었다고 가정.
        driver.quit()
    except BaseException:
        handle_error(driver)    


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
    try:
        driver.find_element_by_id("inputTextView").send_keys(captcha_num)
        driver.find_element_by_xpath("//*[@id='content']/div/div[2]/div[2]/div[2]/a").click()
        WebDriverWait(driver, WAIT_LIMIT_IN_SECONDS).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        
        # 인식이 잘못 되었을 경우
        if has_failed_registration(alert.text):
            handle_error(driver)
    except TimeoutException:
        pass


# alert가 에러 메시지들 포함하고 있으면 에러로 생각.
def has_failed_registration(text):
    # TODO: 정원 초과한 경우 메시지도 추가해야 함. 또 성공했을 때 메시지는 따로 분류해서 성공 알려주고 싶다.
    msgs = {"일치하지", "아닙니다", "종료되었습니다", "만료되었습니다", "로그인 후", "없습니다"}
    
    for msg in msgs:
        if msg in text:
            return True
    return False


# 에러가 생겼을 경우, alert 확인 후 작업 다시 시작.
def handle_error(driver):
    try:
        # alert가 있을 경우 확인해줘야 함.
        WebDriverWait(driver, 1).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
    except TimeoutException:
        pass
    finally:
        # 다시 snipe_vacancy 함수 실행.
        snipe_vacancy(driver)


if __name__ == "__main__":
    # 모델이 경로에 없을 경우 생성해준다.
    if not tf_model_path().exists():
        save_model()

    # 인스턴스 초기 생성. 첫 생성을 시작 때 해서 Register에 걸리는 시간을 줄인다.
    SingletonModel.instance()
    # 드라이버 로딩
    options = webdriver.ChromeOptions()
    # 해상도와 디스플레이 배율에 상관 없이 일관된 화면이 표시되도록 설정.
    options.add_argument("window-size=1920x1080")
    options.add_argument("force-device-scale-factor=1")
    driver = webdriver.Chrome(str(webdriver_path()), options=options)
    driver.implicitly_wait(WAIT_LIMIT_IN_SECONDS)
    
    # 관심강좌 중 빈 자리 탐색하고, 있으면 수강 신청.
    # 모델을 반복적으로 생성하지 않기 위해 메인에서 생성 후 함수 인자로 넘겨준다.
    snipe_vacancy(driver)
    