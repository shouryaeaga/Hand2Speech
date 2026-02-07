import serial
import pandas as pd

df = pd.read_csv('raw_deep_learning_data.csv')
data = df.values.tolist()
if len(data) == 0:
    counter = 0
else:
    counter = data[-1][0]+1

ser = serial.Serial('/dev/ttyACM0', 115200)
print(ser.name)
letter_collecting = 'B'

# features:
# Mean
# Median
# Standard Deviation
# Variance
# Min
# Max
# Range (max-min)
# RMS (root mean square)
# Sum
# Percentiles
# Interquartile range


readings_taken = 0
current_reading = []
reading_thresh = 15
samples = 60

while readings_taken < samples:
    line = ser.readline()
    line = line.decode()
    if line.strip() == "Gesture stopped" and len(current_reading) > reading_thresh:
        counter += 1
        readings_taken += 1
        data.extend(current_reading)
        current_reading = []
        percent = int((readings_taken / samples) * 100)
        print(f"Progress: {readings_taken}/{samples}, or {percent}%")
    elif line.strip() == "Gesture stopped":
        current_reading = []
    else:
        try:
            raw_ax, raw_ay, raw_az, pitch, roll = tuple(line.split())
            current_reading.append([counter, letter_collecting, raw_ax, raw_ay, raw_az, pitch, roll])
        except:
            print("Something went wrong")



df = pd.DataFrame(data, columns=["id", "gesture", "raw_ax", "raw_ay", "raw_az", "pitch", "roll"])
df.to_csv('raw_deep_learning_data.csv', index=False)