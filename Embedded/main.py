from machine import Pin, I2C
import time
from lib import fusion
from mpu6050 import MPU6050

scl = Pin(21)
sda = Pin(20)
button = Pin(11, Pin.IN)

i2c = I2C(0, scl=scl, sda=sda, freq=400000)
devices = i2c.scan()
if len(devices) == 0:
    print("No I2C devices found")
else:
    print("I2C devices found:", [hex(device) for device in devices])

mpu = MPU6050(i2c)

axs, ays, azs, gxs, gys, gzs = [], [], [], [], [], []

offsets = [-0.36, 0.32, 10.72 - 9.81, -3.1, 0.53, -0.74]

fusion = fusion.Fusion()

current_state = button.value()
count = 0
change_state = False
while True:
    new_state = button.value()
    if new_state != current_state:
        current_state = new_state
        change_state = True
    else:
        change_state = False

    raw_ax, raw_ay, raw_az = mpu.read_accelerometer()
    raw_gx, raw_gy, raw_gz = mpu.read_gyroscope()
    # Apply offsets
    raw_ax -= offsets[0]
    raw_ay -= offsets[1]
    raw_az -= offsets[2]
    raw_gx -= offsets[3]
    raw_gy -= offsets[4]
    raw_gz -= offsets[5]

    # CALIBRATION SCRIPT
    # axs.append(raw_ax)
    # ays.append(raw_ay)
    # azs.append(raw_az)
    # gxs.append(raw_gx)
    # gys.append(raw_gy)
    # gzs.append(raw_gz)
    # count += 1
    # if count == 200:
    #     offset_AX = sum(axs) / len(axs)
    #     offset_AY = sum(ays) / len(ays)
    #     offset_AZ = sum(azs) / len(azs)
    #     offset_GX = sum(gxs) / len(gxs)
    #     offset_GY = sum(gys) / len(gys)
    #     offset_GZ = sum(gzs) / len(gzs)

    #     print(f"Offsets: AX={offset_AX:.4f}, AY={offset_AY:.4f}, AZ={offset_AZ:.4f}, GX={offset_GX:.4f}, GY={offset_GY:.4f}, GZ={offset_GZ:.4f}")
    #     break
    # END OF CALIBRATION SCRIPT 
    
    fusion.update_nomag((raw_ax, raw_ay, raw_az), (raw_gx, raw_gy, raw_gz))
    timestamp = time.ticks_ms()

    # print(f">rawAx:{timestamp}:{raw_ax}")
    # print(f">rawAy:{timestamp}:{raw_ay}")
    # print(f">rawAz:{timestamp}:{raw_az}")
    # print(f">rawGx:{timestamp}:{raw_gx}")
    # print(f">rawGy:{timestamp}:{raw_gy}")
    # print(f">rawGz:{timestamp}:{raw_gz}")
    # print(f">pitch:{timestamp}:{fusion.pitch:.2f}")
    # print(f">roll:{timestamp}:{fusion.roll:.2f}")
    # print(f">button:{timestamp}:{current_state}")
    # print("")
    if current_state:
        print(raw_ax, raw_ay, raw_az, fusion.pitch, fusion.roll)
    elif change_state:
        print("Gesture stopped")
        change_state = False
    
    
    time.sleep(0.01)