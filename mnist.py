from __future__ import absolute_import, division, print_function, unicode_literals
import tensorflow as tf
from pathlib import Path
from tensorflow import keras



# MNIST용 간단 모델 생성
def create_model():
    model = tf.keras.models.Sequential([
        keras.layers.Dense(512, activation='relu', input_shape=(784,)),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(10, activation='softmax')
    ])

    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model


if __name__ == "__main__":
    (train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.mnist.load_data()

    train_labels = train_labels
    test_labels = test_labels

    train_images = train_images.reshape(-1, 28 * 28) / 255.0
    test_images = test_images.reshape(-1, 28 * 28) / 255.0

    # 모델 생성 후 학습
    model = create_model()
    model.fit(train_images, train_labels, epochs=5)

    # 파일이 위치한 디렉토리에 학습된 모델 저장
    CURRENT_DIRECTORY = Path(__file__).parent.absolute()
    model.save(str(CURRENT_DIRECTORY / 'mnist.h5')) 

    # 저장된 모델 불러오기
    new_model = tf.keras.models.load_model(str(CURRENT_DIRECTORY / 'mnist.h5'))

    # 모델 구조 요약해서 출력
    new_model.summary()

    # 로드된 모델 평가
    loss, acc = new_model.evaluate(test_images,  test_labels, verbose=2)
    print('Restored model, accuracy: {:5.2f}%'.format(100*acc))
