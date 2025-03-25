import numpy as np
import pandas as pd
import scipy.signal as signal
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import time

# Filtering function: Chebyshev Type II Low-Pass Filter
def chebyshev_filter(signal_data, fs=50, cutoff=0.5, order=4, rs=40):
    """ Apply a 4th-order Chebyshev Type II low-pass filter. """
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    sos = signal.cheby2(order, rs, normal_cutoff, btype='low', analog=False, output='sos')
    return signal.sosfiltfilt(sos, signal_data)

# Peak detection to estimate respiratory rate
def detect_respiratory_peaks(filtered_signal, fs=50):
    peaks, _ = signal.find_peaks(filtered_signal, height=0, distance=fs*1)  # Min 1s spacing
    return peaks

# Compute respiratory rate from detected peaks
def compute_respiratory_rate(peak_indices, window_size=20):
    num_breaths = len(peak_indices)
    return (num_breaths / window_size) * 60  # Convert to breaths per minute

# Real-time plot setup
fig, ax = plt.subplots()
ax.set_title("Live Breathing Signal & Respiratory Rate")
ax.set_xlabel("Time (samples)")
ax.set_ylabel("Amplitude")
line_raw, = ax.plot([], [], 'b', label="Raw Signal")  # Blue - Raw signal
line_filtered, = ax.plot([], [], 'r', label="Filtered Signal")  # Red - Filtered
line_peaks, = ax.plot([], [], 'go', label="Detected Breaths")  # Green dots for peaks
ax.legend()
text_rate = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=12, bbox=dict(facecolor='white', alpha=0.5))  # Respiratory rate display

# File path (Update with actual CSV)
csv_file = "404-imu-data/sensor-on-shirt-chest-5-breadths-big/x-axis1.csv"  

# Parameters
fs = 50  # Sampling frequency (Hz)
window_size = 20  # Window size in seconds
samples_to_read = fs * window_size  # Number of samples to read

# Update function for real-time plotting
def update(frame):
    try:
        df = pd.read_csv(csv_file)
        if len(df) < samples_to_read:
            return

        # Extract latest data (assumes second column = acceleration)
        raw_signal = df.iloc[-samples_to_read:, 1].values  

        print("raw_signal: ", raw_signal)
        time.sleep(1000)

        # Filter the raw signal
        filtered_signal = chebyshev_filter(raw_signal, fs=fs)

        # Detect peaks (breaths)
        peak_indices = detect_respiratory_peaks(filtered_signal, fs)

        # Compute respiratory rate
        respiratory_rate = compute_respiratory_rate(peak_indices, window_size)

        # Update plot
        line_raw.set_data(range(len(raw_signal)), raw_signal)
        line_filtered.set_data(range(len(filtered_signal)), filtered_signal)
        line_peaks.set_data(peak_indices, filtered_signal[peak_indices])  # Plot peaks
        text_rate.set_text(f"Respiratory Rate: {respiratory_rate:.1f} BPM")

        # Adjust axis dynamically
        ax.set_xlim(0, len(raw_signal))
        ax.set_ylim(min(raw_signal) - 0.05, max(raw_signal) + 0.05)

        # 🚨 **Trigger alert if respiratory rate <10 BPM or breath stops >15s**
        if respiratory_rate < 10:
            print("⚠️ WARNING: Respiratory rate dangerously low!")
        if len(peak_indices) == 0:
            print("🚨 ALERT: No detected breaths in last 20s!")

    except Exception as e:
        print("Error:", e)

# Animation function to update the plot in real-time
ani = animation.FuncAnimation(fig, update, interval=1000)  # Update every second
plt.show()
