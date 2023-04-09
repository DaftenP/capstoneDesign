import io
from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment

# audio = AudioSegment.from_file("./test/test_audio.wav")
#
# # Resample the audio to a higher sample rate (e.g., 48000 Hz)
# audio = audio.set_frame_rate(48000)
#
# # Export the resampled audio to a new file
# audio.export("./test/test_audio.wav", format="wav")

def silent(timestamps, audiofile):
    audio_input = AudioSegment.from_file(audiofile, format="wav")
    for start, end in timestamps:
        segment_to_silence = AudioSegment.silent(duration=(end - start))
        audio_input = audio_input[:start] + segment_to_silence + audio_input[end:]
    audio_input.export(audiofile[:-4]+'_output.wav', format="wav")


client = speech.SpeechClient()

audio_file = "./test/test_audio.wav"

with io.open(audio_file, "rb") as f:
    content = f.read()

audio = speech.RecognitionAudio(content=content)

config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    language_code="ko-KR",
    sample_rate_hertz=48000,
    enable_word_time_offsets=True,
)

response = client.recognize(config=config, audio=audio)

# word for filtering
filtering_word = ["무궁화", "화려강산"]
timestamps = []

for result in response.results:
    alternative = result.alternatives[0]

    # whole scripts of stt result
    print(u"Transcript: {}".format(alternative.transcript))
    print(f'example of word : {alternative.words[1]}')
    print("Word level time offsets:")

    for word in alternative.words:
        print(u"word: '{}', start_time: {}, end_time: {}".format(word.word, word.start_time, word.end_time))

        # this point is about conversion.
        if word.word in filtering_word:
            start = str(word.start_time).split(':')
            end = str(word.end_time).split(':')
            timestamps.append([int(int(start[0])*3600000+int(start[1])*60000+float(start[2])*1000),
                               int(int(end[0]) * 3600000 + int(end[1]) * 60000 + float(end[2])*1000)])
silent(timestamps, "./test/test_audio.wav")
print(timestamps)