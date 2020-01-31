import tensorflow as tf
import numpy as np
from tensorflow import keras

from path import tf_model_path



# 모델을 한 번만 생성하기 위해 싱글톤 클래스 사용
class SingletonModel:
    _instance = None

    @classmethod
    def _get_instance(cls):
        return cls._instance
    
    @classmethod
    def instance(cls, *args, **kwargs):
        cls._instance = cls(*args, **kwargs)
        cls.instance = cls._get_instance
        return cls._instance
    
    def __init__(self):
        self._model = tf.keras.models.load_model(str(tf_model_path()))

    @property
    def model(self):
        return self._model


# MNIST 모델 저장
def save_model():
    (train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.mnist.load_data()

    train_labels = train_labels
    test_labels = test_labels

    train_images = train_images.reshape(-1, 28 * 28) / 255.0
    test_images = test_images.reshape(-1, 28 * 28) / 255.0

    # 모델 생성 후 학습
    model = _create_model()
    model.fit(train_images, train_labels, epochs=5)

    # 주어진 경로에 모델 저장.
    model.save(str(tf_model_path()))


# MNIST용 간단 모델 생성
def _create_model():
    model = tf.keras.models.Sequential([
        keras.layers.Dense(512, activation="relu", input_shape=(784,)),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(10, activation="softmax")
    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model
