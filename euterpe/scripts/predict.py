import os
import glob
import traceback

import numpy
from keras.models import load_model
from keras.preprocessing.image import load_img, img_to_array

from euterpe.utils import spectrogram
from euterpe.api import NeteaseMusicAPI

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

    for file in spect_files:
        os.remove(file)

    predictions = [a[0][0] for a in predictions]
    print(predictions)
    print('Moe Confidence: {0:.3%}'.format(numpy.mean(predictions)))
    # pred_sum = sum(a[0][0] for a in predictions)
    # print('{0} confidence.'.format(pct_confidence))


if __name__ == '__main__':
    api = NeteaseMusicAPI()
    while True:
        try:
            song_id = int(input('Input song ID: '))
            res = api.get_song_detail(song_id)
            content = api.get_song_file(song_id)
            print('Song: {0}'.format(res['name']))
            with open('example.mp3', 'wb') as file:
                file.write(content)
            main('example.mp3')
        except Exception as e:
            traceback.print_exc(e)
