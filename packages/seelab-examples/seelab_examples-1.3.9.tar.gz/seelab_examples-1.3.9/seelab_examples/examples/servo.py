import eyes17.eyes
p = eyes17.eyes.open()

import time

for a in range(10):
 p.servo(120)
 time.sleep(0.1)
 p.servo(160)
 time.sleep(0.1)
