import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

original_audio = "./test/test_audio.wav"
modified_audio = "./test/test_audio_output.wav"
# s = sampling (int)
# a = audio signal (numpy array)
s1, a1 = wavfile.read(original_audio)
s2, a2 = wavfile.read(modified_audio)
# plot signal versus time
na1 = a1.shape[0]
la1 = na1 / s1
t1 = np.linspace(0, la1, na1)

na2 = a2.shape[0]
la2 = na2 / s2
t2 = np.linspace(0, la2, na2)

plt.subplot(2,1,1)
plt.plot(t1, a1, 'r-')
plt.ylabel("Original Sound Wave")
plt.subplot(2,1,2)
plt.plot(t2, a2, 'b-')
plt.ylabel("Modified Sound Wave")
plt.xlabel('Time (s)')
plt.show()
