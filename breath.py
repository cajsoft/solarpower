#!/usr/bin/env python
# -*- coding:utf-8 -*-
# -------------------------------
# SDA: Pin3
# SCL: Pin5

import time
import rgb1602
import datetime

lcd=rgb1602.RGB1602(16,2)

def breath(lcd):
    count = range(256)
    for i in count:
        lcd.setRGB(i, 000, i)
        time.sleep(0.005)

    count.reverse()
    for i in count:
        lcd.setRGB(i, 000, i)
        time.sleep(0.005)

if __name__ == '__main__':

    lcd.printout("Breath lights!")

    while True:
        breath(lcd)
