import os
import glob

import numpy
from keras.models import load_model
from keras.preprocessing.image import load_img, img_to_array

from euterpe.utils import spectrogram

FILENAME = 'file.mp3'


def main(input_file: str):
    model = load_model('model.h5')
    print('Analyzing {0}...'.format(input_file))
    spectrogram.convert_to_mono(input_file, 'tmp.mp3')
    spectrogram.audio_to_spect('tmp.mp3', 'spect.png')
    spectrogram.slice_spect('spect.png', 'spect')
    spect_files = glob.glob('spect/*.png')
    images = []
    for item in spect_files:
        img = load_img('{0}'.format(item), target_size=(256, 256))
        img_array = img_to_array(img)
        img_array = numpy.expand_dims(img_array, axis=0)
        img_array /= 255
        images.append(img_array)

    predictions = []
    for image in images:
        prediction = model.predict(image)
        predictions.append(prediction)

    print(predictions)
    pred_sum = sum(a[0] for a in predictions)
    biggest_sum = numpy.amax(pred_sum)
    pct_confidence = round((biggest_sum / sum(pred_sum) * 100), 2)
    pred_class_num = numpy.argmax(pred_sum)

    print('{0} confidence.'.format(pct_confidence))


if __name__ == '__main__':
    main('in_the_end.mp3')
