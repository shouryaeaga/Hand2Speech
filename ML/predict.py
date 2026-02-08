import joblib
model = joblib.load("model.pkl")

import serial
import pandas as pd
import numpy as np

ser = serial.Serial('/dev/ttyACM0', 115200)

readings_taken = 0
reading_thresh = 15

def mean_abs_difference(x):
    mean = np.mean(x)
    return np.mean(np.abs(x-mean))

def magnitude(ax, ay, az):
    return np.sqrt(ax**2 + ay**2 + az**2)

def energy(x):
    return np.sum(x**2)

from scipy.fft import rfft, rfftfreq

def dominant_frequency(x, hz):
    x = x - np.mean(x)
    fft_vals = np.abs(rfft(x))
    freqs = rfftfreq(len(x), 1/hz)
    return freqs[np.argmax(fft_vals[1:]) + 1]

def corr(x, y):
    return np.corrcoef(x, y)[0, 1]

def orientation_features(x):
    return {
        "mean": np.mean(x),
        "std": np.std(x),
        "range": np.max(x) - np.min(x),
        "mad": mean_abs_difference(x)
    }


def accelerometer_features(x, hz):
    return {
        "mean": np.mean(x),
        "std": np.std(x),
        "energy": energy(x),
        "mad": mean_abs_difference(x),
        "dom_freq": dominant_frequency(x, hz)
    }

def extract_features(ax, ay, az, roll, pitch, hz):
    feats = {}

    for name, data in zip(["ax", "ay", "az"], [ax, ay, az]):
        f = accelerometer_features(data, hz)
        for k,v in f.items():
            feats[f"{k}_{name}"] = v

    for name, data in zip(["pitch", "roll"], [pitch, roll]):
        f = orientation_features(data)
        for k,v in f.items():
            feats[f"{k}_{name}"] = v

    mag = magnitude(ax, ay, az)
    feats["mean_mag"] = np.mean(mag)
    feats["std_mag"] = np.std(mag)
    feats["energy_mag"] = energy(mag)

    feats["corr_ax_ay"] = corr(ax, ay)
    feats["corr_ay_az"] = corr(ay, az)
    feats["corr_ax_az"] = corr(ax, az)
    feats["corr_roll_pitch"] = corr(roll, pitch)

    feats["num_samples"] = len(ax)

    return feats

X = pd.DataFrame(columns=[
    # Accelerometer (dynamic)
    "mean_ax", "std_ax", "energy_ax", "mad_ax", "dom_freq_ax",
    "mean_ay", "std_ay", "energy_ay", "mad_ay", "dom_freq_ay",
    "mean_az", "std_az", "energy_az", "mad_az", "dom_freq_az",

    # Orientation (smooth)
    "mean_roll", "std_roll", "range_roll", "mad_roll",
    "mean_pitch", "std_pitch", "range_pitch", "mad_pitch",

    # Magnitude
    "mean_mag", "std_mag", "energy_mag",

    # Correlations
    "corr_ax_ay", "corr_ay_az", "corr_ax_az",
    "corr_roll_pitch",

    # Length
    "num_samples"
])

ax=[]
ay=[]
az=[]
pitch=[]
roll=[]

current_reading = 0

while True:
    line = ser.readline()
    line = line.decode()
    if line.strip() == "Gesture stopped" and current_reading > reading_thresh:
        ax = np.array(ax)
        ay = np.array(ay)
        az = np.array(az)
        pitch = np.array(pitch)
        roll = np.array(roll)
        feats = extract_features(ax, ay, az, roll, pitch, 100)
        X = pd.concat([X, pd.DataFrame([feats])], ignore_index=True)
        print(model.predict(X))
        ax, ay, az, pitch, roll = [], [], [], [], []
        X = X.iloc[0:0]
        current_reading=0
    elif line.strip() == "Gesture stopped":
        ax, ay, az, pitch, roll = [], [], [], [], []
        current_reading = 0
    else:
        try:
            raw_ax, raw_ay, raw_az, raw_pitch, raw_roll = tuple(line.split())
            ax.append(float(raw_ax))
            ay.append(float(raw_ay))
            az.append(float(raw_az))
            pitch.append(float(raw_pitch))
            roll.append(float(raw_roll))
            current_reading+=1
        except:
            print("Something went wrong")