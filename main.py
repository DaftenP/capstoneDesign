import io
from google.cloud import speech_v1p1beta1 as speech

client = speech.SpeechClient()

audio_file = "./test/test_audio.wav"

with io.open(audio_file, "rb") as f:
    content = f.read()

audio = speech.RecognitionAudio(content=content)

config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    language_code="ko-KR",
    enable_word_time_offsets=True,
)

response = client.recognize(config=config, audio=audio)

# word for filtering
filtering_word = ["무궁화", "동해"]

for result in response.results:
    alternative = result.alternatives[0]

    # whole script of stt
    print(u"Transcript: {}".format(alternative.transcript))
    print(f'example for word : {alternative.words[2]}')
    print("Word level time offsets:")

    for word in alternative.words:
        print(u"word: '{}', start_time: {}, end_time: {}".format(word.word, word.start_time, word.end_time))

        # this point is about conversion.
        if word.word in filtering_word:
            print("flag")

