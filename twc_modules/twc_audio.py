import pyaudio
import wave
from twc_modules.configuration import CHUNK_SIZE


def play(wav_filename):
    '''
    Play (on the attached system sound device) the WAV file provided.
    '''
    file = wave.open(wav_filename, 'rb')

    # Instantiate PyAudio.
    p = pyaudio.PyAudio()

    # Open stream.
    stream = p.open(format=p.get_format_from_width(file.getsampwidth()),
                    channels=file.getnchannels(),
                    rate=file.getframerate(),
                    output=True)

    data = file.readframes(CHUNK_SIZE)
    while len(data) > 0:
        stream.write(data)
        data = file.readframes(CHUNK_SIZE)

    # Stop stream.
    stream.stop_stream()
    stream.close()

    # Close PyAudio.
    p.terminate()
