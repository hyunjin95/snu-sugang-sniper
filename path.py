from pathlib import Path


# TensorFLow 모델 경로
def tf_model_path():
    static_directory = static_directory_path()
    model_path = static_directory / "mnist.h5"
    return model_path


# chromedriver 경로
def webdriver_path():
    static_directory = static_directory_path()
    driver_path = static_directory / "chromedriver.exe"
    return driver_path


# static 폴더 경로
def static_directory_path():
    current_directory = project_root_path()
    static_directory = current_directory / "static"
    return static_directory
    

# 현재 파일 위치
def project_root_path():
    return Path(__file__).parent.absolute()