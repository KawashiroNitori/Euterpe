from os import path
from subprocess import run, PIPE
from PIL import Image


DEFAULT_IMG_SIZE = 256
DIR = path.dirname(__file__)


def convert_to_mono(input_file: str, output_file: str):
    command = 'sox {0} {1} remix 1,2'.format(path.join(DIR, input_file), path.join(DIR, output_file))
    run(command, shell=True, stdin=PIPE, stdout=PIPE)
    return output_file 


def audio_to_spect(input_file: str, output_file: str):
    command = 'sox {0} -n spectrogram -Y 300 -X 50 -m -r -o {1}'.format(
        path.join(DIR, input_file), path.join(DIR, output_file))
    run(command, shell=True, stdin=PIPE, stdout=PIPE)
    return output_file


def get_slice_dims(input_img):
    width, height = input_img.size
    num_slices = width // DEFAULT_IMG_SIZE
    offset_px = 0
    image_dims = list(
        map(lambda i: (offset_px + i * DEFAULT_IMG_SIZE, offset_px + (i + 1) * DEFAULT_IMG_SIZE),
            range(num_slices)))
    return image_dims


def slice_spect(input_file: str, output_path: str):
    img_file_cleaned = input_file.replace('.png', '')
    img = Image.open(input_file)
    dims = get_slice_dims(img)
    counter = 0
    for dim in dims:
        counter_formatted = str(counter).zfill(3)
        img_name = '{0}_{1}.png'.format(img_file_cleaned, counter_formatted)
        start_width, end_width = dim
        sliced_img = img.crop((start_width, 0, end_width, DEFAULT_IMG_SIZE))
        sliced_img.save(path.join(output_path, img_name))
        counter += 1
    return output_path

if __name__ == '__main__':
    pass
