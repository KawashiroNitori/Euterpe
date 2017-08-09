from keras import backend
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers.core import Flatten, Dense, Dropout, Activation
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import rmsprop


IMAGE_SIZE = 256
NB_EPOCH = 20
BATCH_SIZE = 64

TRAIN_DATA_DIR = 'data/train'
VALIDATE_DATA_DIR = 'data/validate'

NB_TRAIN_SAMPLES = 196452
NB_VALIDATE_SAMPLES = 60000

if backend.image_data_format() == 'channels_first':
    INPUT_SHAPE = 3, IMAGE_SIZE, IMAGE_SIZE
else:
    INPUT_SHAPE = IMAGE_SIZE, IMAGE_SIZE, 3


def main():
    early_stopping = EarlyStopping(monitor='val_loss', patience=3)
    save_best_model = ModelCheckpoint(filepath='model_{epoch:02d}_{val_loss:.2f}_{val_acc:.3f}.hdf5',
                                      verbose=1, monitor='val_loss')

    model = Sequential()

    model.add(Conv2D(filters=64, kernel_size=2, strides=2, activation='elu', kernel_initializer='glorot_normal',
                     input_shape=INPUT_SHAPE))
    model.add(MaxPooling2D(pool_size=2, padding='same'))

    model.add(Conv2D(filters=128, kernel_size=2, strides=2, activation='elu', kernel_initializer='glorot_normal'))
    model.add(MaxPooling2D(pool_size=2, padding='same'))

    model.add(Conv2D(filters=256, kernel_size=2, strides=2, activation='elu', kernel_initializer='glorot_normal'))
    model.add(MaxPooling2D(pool_size=2, padding='same'))

    model.add(Conv2D(filters=512, kernel_size=2, strides=2, activation='elu', kernel_initializer='glorot_normal'))
    model.add(MaxPooling2D(pool_size=2, padding='same'))

    model.add(Flatten())
    model.add(Dense(128))

    model.add(Activation('elu'))
    model.add(Dropout(0.5))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))
    opt = rmsprop()

    model.compile(loss='binary_crossentropy',
                  optimizer=opt,
                  metrics=['accuracy'])

    train_datagen = ImageDataGenerator(rescale=1. / 255)
    validate_datagen = ImageDataGenerator(rescale=1. / 255)

    train_generator = train_datagen.flow_from_directory(
        TRAIN_DATA_DIR,
        target_size=(IMAGE_SIZE, IMAGE_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='binary'
    )
    validate_generator = validate_datagen.flow_from_directory(
        VALIDATE_DATA_DIR,
        target_size=(IMAGE_SIZE, IMAGE_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='binary'
    )

    history = model.fit_generator(train_generator,
                                  steps_per_epoch=(NB_TRAIN_SAMPLES // BATCH_SIZE),
                                  epochs=NB_EPOCH,
                                  validation_data=validate_generator,
                                  callbacks=[early_stopping, save_best_model],
                                  validation_steps=(NB_VALIDATE_SAMPLES // BATCH_SIZE))

    model.save_weights('full_model_weights.h5')
    model.save('model.h5')


if __name__ == '__main__':
    main()
