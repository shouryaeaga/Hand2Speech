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
letter_collecting = 'A'

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

while readings_taken < 5:
    line = ser.readline()
    line = line.decode()
    print(line.strip())
    if line.strip() == "Gesture stopped":
        counter += 1
        readings_taken += 1
    else:
        try:
            raw_ax, raw_ay, raw_az, pitch, roll = tuple(line.split())
            data.append([counter, letter_collecting, raw_ax, raw_ay, raw_az, pitch, roll])
        except:
            print("Something went wrong")



df = pd.DataFrame(data, columns=["id", "gesture", "raw_ax", "raw_ay", "raw_az", "pitch", "roll"])
df.to_csv('raw_deep_learning_data.csv', index=False)