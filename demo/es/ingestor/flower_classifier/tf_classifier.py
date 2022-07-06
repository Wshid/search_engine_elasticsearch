import numpy as np
import os
import PIL
import tensorflow as tf
import ssl

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

import pathlib

# 약 3천개의 데이터셋
dataset_url = "https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz"
# CNN이 사용하는 레벨 수, 실무에서는 10~20
train_epoch_level = 10
# 학습을 위한 image resize 크기(pixel)
train_img_width = 180
train_img_height = 180

def build_flower_model():
    ssl._create_default_https_context = ssl._create_unverified_context
    data_dir = tf.keras.utils.get_file(
        'flower_photos', origin=dataset_url, untar=True)
    data_dir = pathlib.Path(data_dir)

    image_count = len(list(data_dir.glob('*/*.jpg')))
    print("training image count: " + str(image_count))

    batch_size = 32

    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        data_dir,
        # training:test=0.8:0.2
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(train_img_height, train_img_width),
        batch_size=batch_size)

    # validation step 내부에서도 0.2로 나누어 추가 validation 진행(subset)
    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(train_img_height, train_img_width),
        batch_size=batch_size)

    class_names = train_ds.class_names

    normalization_layer = layers.experimental.preprocessing.Rescaling(1./255)
    normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
    image_batch, labels_batch = next(iter(normalized_ds))
    first_image = image_batch[0]
    # Notice the pixels values are now in `[0,1]`.
    print(np.min(first_image), np.max(first_image))

    num_classes = 5

    # 모델링 과정(Sequential 모델)
    model = Sequential([
        # rescaring
        layers.experimental.preprocessing.Rescaling(
            1./255, input_shape=(train_img_height, train_img_width, 3)),
            # Conv2D 로 training 수행
        layers.Conv2D(16, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(32, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(num_classes)
    ])

    model.compile(optimizer='adam',
                loss=tf.keras.losses.SparseCategoricalCrossentropy(
                    from_logits=True),
                metrics=['accuracy'])

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=train_epoch_level
    )

    # 클래스들과 관련 모델 리턴 
    return class_names, model

# 실제 모델을 사용하여 추론
def predict_class(name, url, class_names, model):
    item_path = tf.keras.utils.get_file(name, origin=url)
    img = keras.preprocessing.image.load_img(
        item_path, target_size=(train_img_height, train_img_width)
    )
    img_array = keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    # 제일 큰 score를 찾아 리턴
    print(
        "This image most likely belongs to {} with a {:.2f} percent confidence."
        .format(class_names[np.argmax(score)], 100 * np.max(score))
    )
    
    # score와 연관된 class 리턴
    return class_names[np.argmax(score)], np.max(score)
