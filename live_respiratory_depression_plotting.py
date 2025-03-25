import numpy as np
import pandas as pd
import scipy.signal as signal
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
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
    peaks, _ = signal.find_peaks(filtered_signal, height=0, distance=fs*3)  # At least 3s apart
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

    return bpm, apnea_detected, peaks

# 📌 Real-Time Monitoring with Live Plotting
def monitor_breathing(fs=50, window_size=10):
    samples_to_read = fs * window_size  # Read last 10 seconds of data

    # Initialize plot
    fig, ax = plt.subplots()
    ax.set_title("Real-Time Respiratory Signal")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Acceleration")
    
    raw_line, = ax.plot([], [], label="Raw Accelerometer Signal", color="gray", alpha=0.5)
    filtered_line, = ax.plot([], [], label="Filtered Respiratory Signal", color="blue")
    peak_dots, = ax.plot([], [], "ro", label="Detected Breaths")
    ax.legend()
    
    def update_plot(frame):
        try:
            # 📌 Read CSV files
            df_x = pd.read_csv(file_x, header=None, names=['X', 'Time'])
            df_y = pd.read_csv(file_y, header=None, names=['Y', 'Time'])
            df_z = pd.read_csv(file_z, header=None, names=['Z', 'Time'])

            if len(df_x) < samples_to_read:
                print("⚠️ Not enough data yet...")
                return raw_line, filtered_line, peak_dots  # Skip update
            
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
            raw_signal = dominant_signal[N:]
            time_data = time_data[N:]

            # 📌 Replace NaN values with 0
            raw_signal = np.nan_to_num(raw_signal, nan=0.0)

            # 📌 Apply Filtering
            filtered_signal = chebyshev_filter(raw_signal, fs=fs)

            # 📌 Compute BPM & detect apnea
            bpm, apnea_detected, peaks = detect_respiratory_depression(filtered_signal, fs)

            # 📌 Print results
            print(f"🫁 Respiratory Rate: {bpm:.2f} BPM  {'🚨 Apnea Detected!' if apnea_detected else ''}")

            # 📌 Update plot
            raw_line.set_data(np.arange(len(raw_signal)), raw_signal)
            filtered_line.set_data(np.arange(len(filtered_signal)), filtered_signal)
            peak_dots.set_data(peaks, filtered_signal[peaks])  # Mark detected breaths
            
            ax.set_xlim(0, len(filtered_signal))  # Adjust x-axis dynamically
            ax.set_ylim(min(filtered_signal) - 0.05, max(filtered_signal) + 0.05)  # Adjust y-axis
            
            return raw_line, filtered_line, peak_dots

        except Exception as e:
            print("Error:", e)
            return raw_line, filtered_line, peak_dots

    ani = animation.FuncAnimation(fig, update_plot, interval=1000)  # Update every second
    plt.show()

# 📌 Run real-time breathing monitor with live plotting
monitor_breathing()
