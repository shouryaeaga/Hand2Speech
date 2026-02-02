from machine import I2C
from utime import sleep_ms
_PWR_MGMT_1 = 0x6B
_GYRO_CONFIG = 0x1B
_ACCEL_CONFIG = 0x1C

_ACCEL_XOUT0 = 0x3B
_ACCEL_XOUT1 = 0x3C
_ACCEL_YOUT0 = 0x3D
_ACCEL_YOUT1 = 0x3E
_ACCEL_ZOUT0 = 0x3F
_ACCEL_ZOUT1 = 0x40

_GYRO_XOUT0 = 0x43
_GYRO_XOUT1 = 0x44
_GYRO_YOUT0 = 0x45
_GYRO_YOUT1 = 0x46
_GYRO_ZOUT0 = 0x47
_GYRO_ZOUT1 = 0x48

GYRO_FULL_SCALE_RANGE = 250
ACCEL_FULL_SCALE_RANGE = 2

GRAVITY = 9.80665  # m/s^2

print("MPU6050 MODULE LOADED")

class MPU6050:
    def __init__(self, i2c: I2C, address=0x68):
        self.i2c = i2c
        self.address = address

        print("INITIATING MPU6050")

        self.ax = 0
        self.ay = 0
        self.az = 0
        self.gx = 0
        self.gy = 0
        self.gz = 0

        try:
            i2c.writeto_mem(self.address, _PWR_MGMT_1, bytes([0x00]))
            sleep_ms(5)
        except Exception:
            print("Could not communicate with MPU6050")
            raise Exception

        self.gyro_config()
        self.accel_config()
        
    def gyro_config(self):
        data = self.i2c.readfrom_mem(self.address, _GYRO_CONFIG, 1)
        fs_sel = (data[0] >> 3) & 0b11
        if fs_sel == 0:
            GYRO_FULL_SCALE_RANGE = 250
        elif fs_sel == 1:
            GYRO_FULL_SCALE_RANGE = 500
        elif fs_sel == 2:
            GYRO_FULL_SCALE_RANGE = 1000
        elif fs_sel == 3:
            GYRO_FULL_SCALE_RANGE = 2000
        print(f"Set gyro full scale range to {GYRO_FULL_SCALE_RANGE} degrees /s")

    def accel_config(self):
        data = self.i2c.readfrom_mem(self.address, _ACCEL_CONFIG, 1)
        afs_sel = (data[0] >> 3) & 0b11
        if afs_sel == 0:
            ACCEL_FULL_SCALE_RANGE = 2
        elif afs_sel == 1:
            ACCEL_FULL_SCALE_RANGE = 4
        elif afs_sel == 2:
            ACCEL_FULL_SCALE_RANGE = 8
        elif afs_sel == 3:
            ACCEL_FULL_SCALE_RANGE = 16
        print(f"Set accel full scale range to {ACCEL_FULL_SCALE_RANGE} g")

    def read_accelerometer(self):
        # read AX
        ax1 = self.i2c.readfrom_mem(self.address, _ACCEL_XOUT0, 1)
        ax2 = self.i2c.readfrom_mem(self.address, _ACCEL_XOUT1, 1)
        # concatenate ax1 onto ax2
        self.ax = (ax1[0] << 8) | ax2[0]
        # read AY
        ay1 = self.i2c.readfrom_mem(self.address, _ACCEL_YOUT0, 1)
        ay2 = self.i2c.readfrom_mem(self.address, _ACCEL_YOUT1, 1)
        # concatenate ay1 onto ay2
        self.ay = (ay1[0] << 8) | ay2[0]
        # read AZ
        az1 = self.i2c.readfrom_mem(self.address, _ACCEL_ZOUT0, 1)
        az2 = self.i2c.readfrom_mem(self.address, _ACCEL_ZOUT1, 1)
        # concatenate az1 onto az2
        self.az = (az1[0] << 8) | az2[0]
        # convert to signed values
        if self.ax > 32767:
            self.ax -= 65536
        if self.ay > 32767:
            self.ay -= 65536
        if self.az > 32767:
            self.az -= 65536
        
        # convert to g
        ax_g = self.ax / (16384.0 * 2 / ACCEL_FULL_SCALE_RANGE)
        ay_g = self.ay / (16384.0 * 2 / ACCEL_FULL_SCALE_RANGE)
        az_g = self.az / (16384.0 * 2 / ACCEL_FULL_SCALE_RANGE)

        self.ax = ax_g * GRAVITY
        self.ay = ay_g * GRAVITY
        self.az = az_g * GRAVITY
        return self.ax, self.ay, self.az
    
    def read_gyroscope(self):
        # read GX
        gx1 = self.i2c.readfrom_mem(self.address, _GYRO_XOUT0, 1)
        gx2 = self.i2c.readfrom_mem(self.address, _GYRO_XOUT1, 1)
        # concatenate gx1 onto gx2
        self.gx = (gx1[0] << 8) | gx2[0]
        # read GY
        gy1 = self.i2c.readfrom_mem(self.address, _GYRO_YOUT0, 1)
        gy2 = self.i2c.readfrom_mem(self.address, _GYRO_YOUT1, 1)
        # concatenate gy1 onto gy2
        self.gy = (gy1[0] << 8) | gy2[0]
        # read GZ
        gz1 = self.i2c.readfrom_mem(self.address, _GYRO_ZOUT0, 1)
        gz2 = self.i2c.readfrom_mem(self.address, _GYRO_ZOUT1, 1)
        # concatenate gz1 onto gz2
        self.gz = (gz1[0] << 8) | gz2[0]
        
        # convert to signed values
        if self.gx > 32767:
            self.gx -= 65536
        if self.gy > 32767:
            self.gy -= 65536
        if self.gz > 32767:
            self.gz -= 65536
        
        # convert to degrees/s
        gx_dps = self.gx / (131 * GYRO_FULL_SCALE_RANGE / 250)
        gy_dps = self.gy / (131 * GYRO_FULL_SCALE_RANGE / 250)
        gz_dps = self.gz / (131 * GYRO_FULL_SCALE_RANGE / 250)

        return gx_dps, gy_dps, gz_dps