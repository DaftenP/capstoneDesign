from google.cloud import speech
from pydub import AudioSegment
import numpy as np
import io


def sample_recognize(local_file_path):
    client = speech.SpeechClient()

    language_code = "ko-KR"
    sample_rate_hertz = 44100

    encoding = speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED
    config = speech.RecognitionConfig(
        sample_rate_hertz=sample_rate_hertz,
        encoding=encoding,
        language_code=language_code,
        enable_word_time_offsets=True,
        use_enhanced=True
    )

    with io.open(local_file_path, "rb") as f:
        content = f.read()

    audio = speech.RecognitionAudio(content=content)

    response = client.recognize(config=config, audio=audio)

    timeline, swear_timeline, words = [], [], []

    sound = AudioSegment.from_file('./test/test_audio.wav', format='wav')

    # Create beep Sound
    def create_beep(duration):
        sps = 44100
        freq_hz = 1000.0
        vol = 0.5

        esm = np.arange(duration / 1000 * sps)
        wf = np.sin(2 * np.pi * esm * freq_hz / sps)
        wf_quiet = wf * vol
        wf_int = np.int16(wf_quiet * 32767)

        beep = AudioSegment(
            wf_int.tobytes(),
            frame_rate=sps,
            sample_width=wf_int.dtype.itemsize,
            channels=1
        )

        return beep

    beep = create_beep(duration=1000)

    # Overlay Partially
    i = 0
    mixed = sound.overlay(beep, position=swear_timeline[i][0], gain_during_overlay=-20)

    # Result
    mixed_final = sound

    for i in range(len(swear_timeline)):
        beep = create_beep(duration=swear_timeline[i][1] - swear_timeline[i][0])
        mixed_final = mixed_final.overlay(beep, position=swear_timeline[i][0], gain_during_overlay=-20)

    mixed_final.export('./test/output.wav', format='wav')