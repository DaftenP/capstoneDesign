from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment
import time

starttime = time.time()


def silent(timestamps, audiofile):
    audio_input = AudioSegment.from_file(audiofile, format="wav")
    for start, end in timestamps:
        segment_to_silence = AudioSegment.silent(duration=(end - start))
        audio_input = audio_input[:start + 1] + segment_to_silence + audio_input[end:]
    audio_input.export(audiofile[:-4] + '_output.wav', format="wav")


client = speech.SpeechClient()

audio_file = "./test/test_audio.wav"

content = AudioSegment.from_file(audio_file, format="wav")
content = content.set_frame_rate(int(content.frame_rate * 1.7))
# with open(audio_file, "rb") as f:
#     content = f.read()
audio = speech.RecognitionAudio(content=content.raw_data)

config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    language_code="ko-KR",
    sample_rate_hertz=25600,
    enable_word_time_offsets=True,
)

response = client.recognize(config=config, audio=audio)
# word for filtering
filtering_word = ["새끼"]
timestamps = []
data = []
for result in response.results:
    alternative = result.alternatives[0]

    # whole scripts of stt result
    # print(u"Transcript: {}".format(alternative.transcript))
    # print(f'example of word : {alternative.words[1]}')
    # print("Word level time offsets:")

    for word in alternative.words:
        # data.append([word.word, word.start_time, word.end_time])
        # this point is about conversion.
        start = str(word.start_time).split(':')
        end = str(word.end_time).split(':')
        start_time = int(int(start[0]) * 3600000 + int(start[1]) * 60000 + float(start[2]) * 1000)
        end_time = int(int(end[0]) * 3600000 + int(end[1]) * 60000 + float(end[2]) * 1000)
        timestamps.append([start_time,end_time])
        if word.word in filtering_word:
            print(f'------A filtering word was detected------')
            print(u"word: '{}', time: {}ms ~ {}ms".format(word.word, start_time, end_time))
            print(f'-----------------------------------------')
        else:
            print(u"word: '{}', time: {}ms ~ {}ms".format(word.word, start_time, end_time))
endtime = time.time()
# print(f"Running time : {endtime - starttime:.5f} sec")
# silent(timestamps, "./test/test_audio.wav")
# print(f"Timestamp of filtered words : {timestamps}")
# with open('data.csv', 'w') as f:
#     for d, s, e in data:
#         f.write(f'{d},{s},0\n')
#         f.write(f'{d},{e},0\n')
