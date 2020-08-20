# -*- coding: utf-8 -*-

import time
import threading
import Queue

# for motor control
import RPi.GPIO as GPIO
from time import sleep

en_a = 18
in_1 = 23
in_2 = 24
en_b = 16
in_3 = 12
in_4 = 25
mot_l = None
mot_r = None

def initMotors():
    global mot_l, mot_r

    # for motor control
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(en_a, GPIO.OUT)
    GPIO.setup(in_1, GPIO.OUT)
    GPIO.setup(in_2, GPIO.OUT)
    GPIO.setup(en_b, GPIO.OUT)
    GPIO.setup(in_3, GPIO.OUT)
    GPIO.setup(in_4, GPIO.OUT)

    # For PWM
    mot_l = GPIO.PWM(en_a, 50)  #
    mot_r = GPIO.PWM(en_b, 50)  #
    mot_l.start(0)
    mot_r.start(0)

def calcDutyCycle(speed_level):
  # the input level should be 1-10.
  if speed_level == 0:
    return 0
  else:
    dc = 20 + 15*(abs(speed_level/2))
    return dc

def pwmControlDualMotor(l_motor, r_motor):
  if l_motor == 0:
    mot_l.ChangeDutyCycle(0)
  elif l_motor > 0:
    GPIO.output(in_1, True) # counterwise
    GPIO.output(in_2, False)
    dc = calcDutyCycle(int(l_motor))
    print('left motor speed level:', l_motor)
    print('left motor duty cycle is:', dc)
    mot_l.ChangeDutyCycle(dc)
  else:
    GPIO.output(in_1, False) # anti-counterwise
    GPIO.output(in_2, True)
    dc = calcDutyCycle(int(l_motor))
    print('left motor speed level:', l_motor)
    print('left motor duty cycle is:', dc)
    mot_l.ChangeDutyCycle(dc)

  if r_motor == 0:
    mot_r.ChangeDutyCycle(0)
  elif r_motor > 0:
    GPIO.output(in_3, True) # counterwise
    GPIO.output(in_4, False)
    dc = calcDutyCycle(int(r_motor))
    print('right motor speed level:', r_motor)
    print('right motor duty cycle is:', dc)
    mot_r.ChangeDutyCycle(dc)
  else:
    GPIO.output(in_3, False) # anti-counterwise
    GPIO.output(in_4, True)
    dc = calcDutyCycle(int(r_motor))
    print('right motor speed level:', r_motor)
    print('right motor duty cycle is:', dc)
    mot_r.ChangeDutyCycle(dc)

'''
def stop():
    GPIO.output(en_a, False)
    GPIO.output(en_b, False)

def forward():
    GPIO.output(en_a, True)
    GPIO.output(in_1, True)
    GPIO.output(in_2, False)
    GPIO.output(en_b, True)
    GPIO.output(in_3, True)
    GPIO.output(in_4, False)
    sleep(1.5)
    stop()

def backward():
    GPIO.output(en_a, True)
    GPIO.output(in_1, False)
    GPIO.output(in_2, True)
    GPIO.output(en_b, True)
    GPIO.output(in_3, False)
    GPIO.output(in_4, True)
    sleep(1)
    stop()

def turn_right():
    GPIO.output(en_a, True)
    GPIO.output(in_1, True)
    GPIO.output(in_2, False)
    GPIO.output(en_b, True)
    GPIO.output(in_3, False)
    GPIO.output(in_4, True)
    sleep(0.3)
    stop()

def turn_left():
    GPIO.output(en_a, True)
    GPIO.output(in_1, False)
    GPIO.output(in_2, True)
    GPIO.output(en_b, True)
    GPIO.output(in_3, True)
    GPIO.output(in_4, False)
    sleep(0.3)
    stop()
'''

class MotorThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'Motor Control Thread'
        self.do_job = True
        self.queue = Queue.Queue()
        self.lock = threading.Lock()
        initMotors()

    def run(self):
        print('Starting', self.name)
        while self.do_job:
            # Check Message Queue
            if self.queue.qsize() > 0:
                l_speed, r_speed = self.queue.get()
                print("l_speed: %d, r_speed: %d" % (l_speed, r_speed))
                #print("%s got message: %s" % (self.name, rcv_msg))
                pwmControlDualMotor(l_speed, r_speed) # driving motors

    def stop_job(self):
        print('Exit %s' % (self.name))
        self.do_job = False

    def set_speed(self, l_speed, r_speed):
        self.queue.put((l_speed, r_speed))
