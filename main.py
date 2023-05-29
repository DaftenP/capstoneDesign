import pyaudio
import numpy as np
from recognizer import recognize

# 파이오디오 초기화
CHUNK = 1024  # 오디오 데이터를 한 번에 읽을 크기
FORMAT = pyaudio.paInt16  # 오디오 포맷
CHANNELS = 1  # 오디오 채널 (모노: 1, 스테레오: 2)
RATE = 16000  # 샘플링 레이트 (Hz)

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# 녹음 시작
print("녹음을 시작합니다.")

buffer = []  # 음성 데이터를 저장할 버퍼
is_recording = False  # 녹음 중인지 여부를 나타내는 플래그

while True:
    data = stream.read(CHUNK)
    audio_data = np.frombuffer(data, dtype=np.int16)

    # 음성 데이터의 RMS 값을 계산하여 묵음인지 여부를 판단
    rms = np.sqrt(np.mean(np.square(audio_data)))
    if rms < 1000:  # 임계값을 조정하여 묵음 판단 기준 설정
        if is_recording:
            is_recording = False
            print("녹음이 종료되었습니다.", buffer)
            await recognize(buffer)
            buffer = []  # 버퍼 초기화
    else:
        if not is_recording:
            is_recording = True
            print("녹음을 시작합니다.")

    if is_recording:
        buffer.append(audio_data.tobytes())  # 버퍼에 음성 데이터 추가

# 종료 시 정리 작업
stream.stop_stream()
stream.close()
p.terminate()