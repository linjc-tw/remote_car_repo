# -*- coding: utf-8 -*-

import time
import threading
import Queue

# for motor control
import RPi.GPIO as GPIO

en_a = 18
in_1 = 23
in_2 = 24
en_b = 16
in_3 = 12
in_4 = 25

class MotorThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'Motor Control Thread'
        self.do_job = True
        self.queue = Queue.Queue()
        self.lock = threading.Lock()
        self.mot_l = None
        self.mot_r = None
        self.__initMotors()

    def run(self):
        print('Starting', self.name)
        while self.do_job:
            # Check Message Queue
            if self.queue.qsize() > 0:
                l_speed, r_speed = self.queue.get()
                print("l_speed: %d, r_speed: %d" % (l_speed, r_speed))
                #print("%s got message: %s" % (self.name, rcv_msg))
                self.__pwmControlDualMotor(l_speed, r_speed) # driving motors

    def __initMotors(self):
        # for motor control
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(en_a, GPIO.OUT)
        GPIO.setup(in_1, GPIO.OUT)
        GPIO.setup(in_2, GPIO.OUT)
        GPIO.setup(en_b, GPIO.OUT)
        GPIO.setup(in_3, GPIO.OUT)
        GPIO.setup(in_4, GPIO.OUT)

        # For PWM
        self.mot_l = GPIO.PWM(en_a, 50)  #
        self.mot_r = GPIO.PWM(en_b, 50)  #
        self.mot_l.start(0)
        self.mot_r.start(0)

    def __pwmControlDualMotor(self, l_motor, r_motor):
        def calcDutyCycle(speed_level):
            # the input level should be 1-10.
            if speed_level == 0:
                return 0
            else:
                dc = 20 + 15*(abs(speed_level/2))
            return dc

        if l_motor == 0:
            dc = 0
        elif l_motor > 0:
            GPIO.output(in_1, True) # counterwise
            GPIO.output(in_2, False)
            dc = calcDutyCycle(int(l_motor))
        else:
            GPIO.output(in_1, False) # anti-counterwise
            GPIO.output(in_2, True)
            dc = calcDutyCycle(int(l_motor))

        if r_motor == 0:
            dc = 0
        elif r_motor > 0:
            GPIO.output(in_3, True) # counterwise
            GPIO.output(in_4, False)
            dc = calcDutyCycle(int(r_motor))
        else:
            GPIO.output(in_3, False) # anti-counterwise
            GPIO.output(in_4, True)
            dc = calcDutyCycle(int(r_motor))

        print('left motor speed level:', l_motor)
        print('left motor duty cycle is:', dc)
        print('right motor speed level:', r_motor)
        print('right motor duty cycle is:', dc)

        self.mot_l.ChangeDutyCycle(dc)
        self.mot_r.ChangeDutyCycle(dc)

    def stop_job(self):
        print('Exit %s' % (self.name))
        self.do_job = False

    def set_speed(self, l_speed, r_speed):
        self.queue.put((l_speed, r_speed))


# test
def test():
    from time import sleep
    print('Running Motor Test...')
    motor_thread = MotorThread()
    motor_thread.start()

    motor_thread.set_speed(10, 10)
    sleep(1)
    motor_thread.set_speed(-10, -10)
    sleep(1)
    motor_thread.set_speed(-10, 10)
    sleep(1)
    motor_thread.set_speed(10, -10)
    sleep(1)
    motor_thread.set_speed(0, 0)
    sleep(1)

    # Leave Test
    motor_thread.stop_job()
    motor_thread.join()

#test()
