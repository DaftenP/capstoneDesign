import io

import pyaudio
from queue import Queue
import threading
import numpy as np
from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment
from flask import Flask, Response, render_template
import time

app = Flask(__name__)

# 버퍼 크기 및 샘플링 관련 설정
BUFFER_SIZE = 1024  # 버퍼 크기 (조정 가능)
SAMPLE_RATE = 16000  # 샘플링 레이트 (16000Hz로 설정)

# 버퍼 생성 및 묵음 기준 임계값 설정
buffer = Queue()
stream_buffer = Queue()
SILENCE_THRESHOLD = 1500  # 묵음 임계값 (조정 가능) // default = 300

client = speech.SpeechClient()
audio = pyaudio.PyAudio()
count = 0


# 마이크로 음성 캡처 및 처리를 위한 스레드
def audio_capture():
    # 마이크로 음성 입력 설정
    stream = audio.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=SAMPLE_RATE,
                        input=True,
                        frames_per_buffer=BUFFER_SIZE,
                        )

    while True:
        data = stream.read(BUFFER_SIZE)
        audio_data = np.frombuffer(data, dtype=np.int16)
        # 묵음 판별
        is_silence = np.max(np.abs(audio_data)) < SILENCE_THRESHOLD

        if is_silence:
            # 묵음이 아닌 경우 버퍼에 있는 데이터를 인식 스레드로 전달
            if len(buffer.queue) > 20:
                buffer_data = np.concatenate(list(buffer.queue))
                buffer.queue.clear()
                recognition_thread = threading.Thread(target=speech_recognition, args=(buffer_data,))
                recognition_thread.start()
        buffer.put(audio_data)

    stream.stop_stream()
    stream.close()
    audio.terminate()


# 음성 인식을 위한 스레드
def speech_recognition(audio_data):
    # while True:

    # 버퍼에 있는 음성 데이터를 바이너리로 변환
    audio_binary = audio_data.tobytes()
    # Google Cloud STT에 전송할 요청 객체 생성
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code="ko-KR",
        enable_word_time_offsets=True,
    )
    audio = speech.RecognitionAudio(content=audio_binary)

    # 인식 요청 전송
    response = client.recognize(config=config, audio=audio)
    # print(response.results)
    # 인식 결과 출력
    filtering_word = ["바보", '바보야']

    timestamps = []
    for result in response.results:
        alternative = result.alternatives[0]
        for word in alternative.words:
            # this point is about conversion.
            start = str(word.start_time).split(':')
            end = str(word.end_time).split(':')
            start_time = int(int(start[0]) * 3600000 + int(start[1]) * 60000 + float(start[2]) * 1000)
            end_time = int(int(end[0]) * 3600000 + int(end[1]) * 60000 + float(end[2]) * 1000)
            if word.word in filtering_word:
                timestamps.append([start_time, end_time])
                print(f'------A filtering word was detected------')
                print(u"word: '{}', time: {}ms ~ {}ms".format(word.word, start_time, end_time))
                print(f'-----------------------------------------')
            else:
                print(u"word: '{}', time: {}ms ~ {}ms".format(word.word, start_time, end_time))
    silent_thread = threading.Thread(target=set_silent, args=(timestamps, audio_binary,))
    silent_thread.start()
    # print(f"Timestamp of filtered words : {timestamps}")


def set_silent(timestamps, audio_data):
    global count
    audio_input = AudioSegment(audio_data, frame_rate=SAMPLE_RATE, channels=1,
                               sample_width=audio.get_sample_size(pyaudio.paInt16))
    for start, end in timestamps:
        segment_to_silence = AudioSegment.silent(duration=(end - start))
        audio_input = audio_input[:start + 1] + segment_to_silence + audio_input[end:]
    audio_input.export('./output/' + str(count).zfill(6) + '_output.wav', format="wav")
    stream_buffer.put('./output/' + str(count).zfill(6) + '_output.wav')
    count += 1
    # stream_buffer.put(audio_input)


# 마이크로 음성 캡처 스레드 시작
capture_thread = threading.Thread(target=audio_capture)
capture_thread.daemon = True
capture_thread.start()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/stream')
def audio_stream():
    def generate():
        while True:
            path = stream_buffer.get()
            with open(path, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    yield data
        # while True:
        # if len(stream_buffer.queue) > 5:
        #     data = b''.join(list(stream_buffer.queue))
        #     stream_buffer.queue.clear()
        #     yield data

    return Response(generate(), mimetype="audio/wav")


# 프로그램이 종료될 때까지 대기
try:
    if __name__ == '__main__':
        app.run(debug=True)
    while True:
        pass
except KeyboardInterrupt:
    pass
