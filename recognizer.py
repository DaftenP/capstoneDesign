from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment
import time




def set_silent(timestamps, audiofile):
    audio_input = AudioSegment(audiofile, frame_rate=16000)
    for start, end in timestamps:
        segment_to_silence = AudioSegment.silent(duration=(end - start))
        audio_input = audio_input[:start + 1] + segment_to_silence + audio_input[end:]
    audio_input.export('./test/' + time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime()) + '_output.wav', format="wav")


async def recognize(audio_data):
    for data in audio_data:
        client = speech.SpeechClient()

        audio = speech.RecognitionAudio(content=data)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code="ko-KR",
            sample_rate_hertz=25600,
            enable_word_time_offsets=True,
        )
        response = client.recognize(config=config, audio=audio)

        # [word for filtering]
        filtering_word = ["새끼"]

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
        set_silent(timestamps, data)
        print(f"Timestamp of filtered words : {timestamps}")
