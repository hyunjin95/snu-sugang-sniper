# 서울대학교 수강신청 빈자리 자동 수강신청 스크립트

관심강좌 1페이지에 있는 강좌들 중 빈 강의가 있으면 자동 신청

- 동작 과정
  1. `TensorFlow` 이용해서 `MNIST` 데이터셋으로 트레이닝한 모델 저장
  2. `Selenium`, `BeautifulSoup4`를 이용해서 수강신청 사이트 크롤링
  3. `OpenCV` 이용해서 수강신청 확인문자 이미지 추출 후 전처리
  4. 저장되어 있는 모델을 이용해서 이미지에서 숫자 추출
  5. 수강 신청!

- 실행 환경
  - OS: `Windows 10 64bit 19H2`
  - 시기: 2020년 2월

## 사용 방법

1. 레포 다운 후 필요한 툴과 pip 패키지들 설치

    툴: `ChromeDriver(폴더에 포함)`, `Python 3.7`

    ```shell
    pip install --upgrade TensorFlow
    pip install bs4 selenium opencv-python
    ```

2. `sugang.py` 에서 전역 변수들(`USER_ID`, `USER_PW`, `EXCLUDE_JUNIORS`, `REFRESH_INTERVAL_IN_SECONDS`, `WAIT_LIMIT_IN_SECONDS`) 설정
3. `sugang.py` 실행

## 개발 환경

`Windows 10 64bit 19H2`, [`Python 3.7.6`](https://www.python.org/downloads/release/python-376/), [`ChromeDriver 79.0.3945.36`](https://chromedriver.chromium.org/downloads), [`TensorFlow 2.0`](https://www.tensorflow.org/install)
