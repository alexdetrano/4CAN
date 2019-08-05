#!/usr/bin/env python
import RPi.GPIO as GPIO

# use physical pin numbers
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# LEDs initally all off
GPIO.setup(29,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(31,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(33,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(37,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(13,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(07,GPIO.OUT,initial=GPIO.LOW)

# B
raw_input('press enter and B should turn green')
GPIO.output(29, GPIO.HIGH)
GPIO.output(31, GPIO.LOW)

raw_input('press enter and B should turn red ')
GPIO.output(29, GPIO.LOW)
GPIO.output(31, GPIO.HIGH)

# A
raw_input('press enter and A should turn green')
GPIO.output(33, GPIO.HIGH)
GPIO.output(37, GPIO.LOW)

raw_input('press enter and A should turn red ')
GPIO.output(33, GPIO.LOW)
GPIO.output(37, GPIO.HIGH)

# C
raw_input('press enter and C should turn green')
GPIO.output(13, GPIO.HIGH)

# D
raw_input('press enter and D should turn green')
GPIO.output(07, GPIO.HIGH)

raw_input('press enter and all should turn off')
GPIO.setup(29,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(31,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(33,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(37,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(13,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(07,GPIO.OUT,initial=GPIO.LOW)
