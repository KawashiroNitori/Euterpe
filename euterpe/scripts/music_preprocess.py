import threading
import threadpool
import json
from os import path

from euterpe import errors
from euterpe.utils import spectrogram
from euterpe.api import NeteaseMusicAPI

downloaded_set = set()
lock = threading.Lock()

DIR = path.dirname(__file__)
STEREO_PATH = path.join(DIR, 'tmp/music/stereo/{0}.mp3')
MONO_PATH = path.join(DIR, 'tmp/music/mono/{0}.mp3')
SPECTROGRAM_PATH = path.join(DIR, 'tmp/spectrogram/{0}.png')
SLICED_PATH = path.join(DIR, 'tmp/spectrogram/sliced')


def write(file_path: str, content):
    with open(file_path, 'wb') as file:
        file.write(content)


def process(song_id: int):
    with lock:
        global downloaded_set
        if song_id in downloaded_set:
            print('{0} skipped.'.format(song_id))
            return
        downloaded_set.add(song_id)
    try:
        song_info = NeteaseMusicAPI().get_song_detail(song_id)['songs'][0]
        print('Downloading {0}_{1}...'.format(song_id, song_info['name']))
        content = NeteaseMusicAPI().get_song_file(song_id)
    except errors.NotFoundError:
        print('{0} not found, skipped.'.format(song_id))
        return
    write(STEREO_PATH.format(song_id), content)
    print('Converting {0}_{1} to mono...'.format(song_id, song_info['name']))
    spectrogram.convert_to_mono(STEREO_PATH.format(song_id), MONO_PATH.format(song_id))
    print('Generating {0}_{1} to spectrogram...'.format(song_id, song_info['name']))
    spectrogram.audio_to_spect(MONO_PATH.format(song_id), SPECTROGRAM_PATH.format(song_id))
    spectrogram.slice_spect(SPECTROGRAM_PATH.format(song_id), SLICED_PATH)
    print('{0}_{1} finished.'.format(song_id, song_info['name']))


if __name__ == '__main__':
    with open(path.join(DIR, 'data.json'), 'r') as file:
        downloaded_set = set(json.loads(file.read()))
    playlists = [436692330, 820024779, 759037438, 864906545, 760741533, 734141330, 646816490, 637566851,
                 646548465, 565589926, 584365345, 551869937, 543948959, 557709307, 112513428, 396761834]
    songs = []
    pool = threadpool.ThreadPool(4)
    # req = threadpool.makeRequests(process, )
    for playlist in playlists:
        info = NeteaseMusicAPI().get_playlist_detail(playlist)
        songs += [item['id'] for item in info['playlist']['tracks']]
    print('{0} songs.'.format(len(set(songs))))
    reqs = threadpool.makeRequests(process, songs)
    [pool.putRequest(req) for req in reqs]
    pool.wait()
    with open(path.join(DIR, 'data.json'), 'w') as file:
        file.write(json.dumps(list(downloaded_set)))
