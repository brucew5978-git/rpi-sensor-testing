import numpy as np
import pandas as pd
import scipy.signal as signal
import time
from pathlib import Path

# 📌 Folder containing CSV files
folder_path = "./"
file_x = folder_path + "x-axis.csv"
file_y = folder_path + "y-axis.csv"
file_z = folder_path + "z-axis.csv"

# 📌 Chebyshev Type II Low-Pass Filter
def chebyshev_filter(signal_data, fs=50, cutoff=0.5, order=4, rs=40):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    sos = signal.cheby2(order, rs, normal_cutoff, btype='low', analog=False, output='sos')
    return signal.sosfiltfilt(sos, signal_data)

# 📌 Detect Breathing Rate (BPM) using Peak Detection
def detect_breathing_rate(filtered_signal, fs=50):
    peaks, _ = signal.find_peaks(filtered_signal, height=0, distance=fs*2)  # At least 2s apart
    duration_in_minutes = len(filtered_signal) / (fs * 60)
    if duration_in_minutes == 0:
        return 0, peaks  # Prevent division by zero
    breathing_rate = len(peaks) / duration_in_minutes  # BPM formula
    return breathing_rate, peaks

# 📌 Detect Respiratory Depression (BPM < 10 or apnea > 15s)
def detect_respiratory_depression(filtered_signal, fs=50):
    bpm, peaks = detect_breathing_rate(filtered_signal, fs)
    apnea_detected = False
    if len(peaks) > 1:
        peak_intervals = np.diff(peaks) / fs  # Convert to seconds
        if np.any(peak_intervals > 15):
            apnea_detected = True

    # 🚨 Alerts
    if bpm < 10:
        print("⚠️ Bradypnea Detected: BPM =", bpm)
    if apnea_detected:
        print("🚨 Apnea Detected: No breath for > 15 sec!")

    return bpm, apnea_detected

# 📌 Live Monitoring Function
def monitor_breathing(fs=50, window_size=10):
    samples_to_read = fs * window_size  # Read last 20 seconds of data

    while True:
        try:
            # 📌 Read CSV files
            df_x = pd.read_csv(file_x, header=None, names=['X', 'Time'])
            df_y = pd.read_csv(file_y, header=None, names=['Y', 'Time'])
            df_z = pd.read_csv(file_z, header=None, names=['Z', 'Time'])

            if len(df_x) < samples_to_read:
                print("⚠️ Not enough data yet...")
                time.sleep(1)
                continue

            # 📌 Extract recent data
            time_data = df_x['Time'].iloc[-samples_to_read:]
            x = df_x['X'].iloc[-samples_to_read:]
            y = df_y['Y'].iloc[-samples_to_read:]
            z = df_z['Z'].iloc[-samples_to_read:]

            # 📌 Determine dominant axis
            p2p_x, p2p_y, p2p_z = np.ptp(x), np.ptp(y), np.ptp(z)
            dominant_signal = x if p2p_x > p2p_y and p2p_x > p2p_z else (y if p2p_y > p2p_x and p2p_y > p2p_z else z)

            # 📌 Skip first N values (remove noisy startup data)
            N = 3
            dominant_signal = dominant_signal[N:]
            time_data = time_data[N:]

            # 📌 Replace NaN values with 0
            dominant_signal = np.nan_to_num(dominant_signal, nan=0.0)

            # 📌 Apply Filtering
            filtered_signal = chebyshev_filter(dominant_signal, fs=fs)

            # 📌 Compute BPM & detect apnea
            bpm, apnea_detected = detect_respiratory_depression(filtered_signal, fs)

            # 📌 Print results
            print(f"🫁 Respiratory Rate: {bpm:.2f} BPM  {'🚨 Apnea Detected!' if apnea_detected else ''}")

            # 📌 Wait for 1 second before next update
            time.sleep(1)

        except Exception as e:
            print("Error:", e)
            break

# 📌 Run real-time breathing monitor
monitor_breathing()
