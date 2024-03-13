import struct
import time

import serial

# 设置串口参数
port = '/dev/ttyUSB0'  # 串口设备路径
baudrate = 19200  # 波特率

# 创建串口对象
ser = serial.Serial(port, baudrate, timeout=1)

# 设置ID
setId1 = b'\x01\x10\x10\x11\x00\x01\x02\x01\x00\x40\xB5'
setId2 = b'\x01\x10\x10\x11\x00\x01\x02\x02\x00\xB0\xB5'
setId3 = b'\x01\x10\x10\x11\x00\x01\x02\x03\x00\x20\xB4'
setId4 = b'\x01\x10\x10\x11\x00\x01\x02\x04\x00\x10\xB6'
setId5 = b'\x01\x10\x10\x11\x00\x01\x02\x05\x00\x80\xB7'
setId6 = b'\x01\x10\x10\x11\x00\x01\x02\x06\x00\x70\xB7'
# ser.write(setId1)
# ser.write(setId2)
# ser.write(setId3)
# ser.write(setId4)
# ser.write(setId5)
# ser.write(setId6)
data = ser.read(8)
print(data)

# 读取命令-
# b'\x01\x03\x00\x05\x00\x0D\x0E\x94',  #id1
# b'\x02\x03\x00\x05\x00\x0D\x3D\x94',  #id2
# b'\x03\x03\x00\x05\x00\x0D\xEC\x95',  #id3
# b'\x04\x03\x00\x05\x00\x0D\x5B\x94',  #id4
# b'\x05\x03\x00\x05\x00\x0D\x8A\x95',  #id5
# b'\x06\x03\x00\x05\x00\x0D\xB9\x95',  #id6

# cmd = [b'\x01\x03\x00\x05\x00\x0D\x0E\x94',
#        b'\x02\x03\x00\x05\x00\x0D\x3D\x94',
#        b'\x03\x03\x00\x05\x00\x0D\xEC\x95',
#        b'\x04\x03\x00\x05\x00\x0D\x5B\x94', ]

cmd = [b'\x01\x03\x00\x05\x00\x0D\x0E\x94']

# filelists = ['id1.txt', 'id2.txt', 'id3.txt', 'id4.txt']
#
# for index in range(len(filelists)):
#     with open(filelists[index], 'w') as file:
#         file.write("")
#         file.close()

while True:
    index = 0
    ser.write(cmd[index])
    data = ser.read(32)
    if (len(data) == 32):
        hex_data = ' '.join([hex(x) for x in data[4:30]])
        uint16_array = struct.unpack('>' + 'H' * (len(data[4:30]) // 2), bytes(data[4:30]))
        print(index + 1, uint16_array)
    time.sleep(1)
