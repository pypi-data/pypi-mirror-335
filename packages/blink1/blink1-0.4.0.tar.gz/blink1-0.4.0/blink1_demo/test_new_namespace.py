#!/usr/bin/env python

"""
demo_pattern3 -- demo of blink1 library color pattern parsing
"""
import time,sys
#from blink1.blink1 import Blink1  # old

# import blink1
# try:
#     b1 = blink1.Blink1()
# except blink1.Blink1ConnectionFailed as e:
#     print("dangit,",e)
#     sys.exit(1)

from blink1 import Blink1, Blink1ConnectionFailed
b1 = Blink1()

b1.fade_to_color(100,'green')
time.sleep(1)
b1.fade_to_color(100,'black')
