import matplotlib.pyplot as plt
import numpy as np

N = 100
n = np.arange(N)
hanning_window = 0.5 * (1 - np.cos(2 * np.pi * n / (N - 1)))

plt.plot(n, hanning_window)
plt.title("Hanning Window")
plt.xlabel("Sample")
plt.ylabel("Amplitude")
plt.grid(True)
plt.show()
