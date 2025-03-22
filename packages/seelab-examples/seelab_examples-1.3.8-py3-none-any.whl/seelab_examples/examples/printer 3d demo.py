import eyes17.eyes as eyes
p = eyes.open(port='/dev/ttyACM0')

# This program requires a 3D printer with a laser and a motor.
# It will move the laser in a back and forth pattern.

import serial, time

print(p.get_voltage('A1'))

laser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)
time.sleep(0.2)
print('residual data', laser.read())

laser.write(b'G0 F20000\n')  # Motor speed

x=0
y=0
laser.write(f'G0 X{x} Y{y}\n'.encode('utf-8'))
time.sleep(1)

for a in range(10):
    print('fwd')
    laser.write(f'G0 X{150} Y{0} Z0\n'.encode('utf-8'))
    time.sleep(1)
    print('back')
    laser.write(f'G0 X{0} Y{0} Z0\n'.encode('utf-8'))
    time.sleep(1)
