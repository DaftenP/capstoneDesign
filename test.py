import whisper
import time

start = time.time()
model = whisper.load_model("base")
result = model.transcribe("./test/test_audio_original.wav")
print(result)
end = time.time()

print(f"{end - start:.5f} sec")