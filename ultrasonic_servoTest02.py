import RPi.GPIO as GPIO
import time
from time import sleep
from multiprocessing import Process

GPIO.setwarnings(False) 
print("AkibaTV HC-SR04 Start")

GPIO.setmode(GPIO.BCM)

STOP  = 0
FORWARD  = 1
BACKWORD = 2

CH1 = 0
CH2 = 1

OUTPUT = 1
INPUT = 0

HIGH = 1
LOW = 0

ENA = 26  
ENB = 0   

IN1 = 19  
IN2 = 13  
IN3 = 6   
IN4 = 5   

pwm_gpio = 21
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.IN)
GPIO.setup(pwm_gpio, GPIO.OUT)
pwm = GPIO.PWM(pwm_gpio, 50)


def setPinConfig(EN, INA, INB):        
    GPIO.setup(EN, GPIO.OUT)
    GPIO.setup(INA, GPIO.OUT)
    GPIO.setup(INB, GPIO.OUT) 
    pwm = GPIO.PWM(EN, 100)   
    pwm.start(0) 
    return pwm


def setMotorContorl(pwm, INA, INB, speed, stat):
    pwm.ChangeDutyCycle(speed)  
    
    if stat == FORWARD:
        GPIO.output(INA, HIGH)
        GPIO.output(INB, LOW)
        
    elif stat == BACKWORD:
        GPIO.output(INA, LOW)
        GPIO.output(INB, HIGH)        

    elif stat == STOP:
        GPIO.output(INA, LOW)
        GPIO.output(INB, LOW)

def setMotor(ch, speed, stat):
    if ch == CH1:
        setMotorContorl(pwmA, IN1, IN2, speed, stat)
    else:
        setMotorContorl(pwmB, IN3, IN4, speed, stat)

pwmA = setPinConfig(ENA, IN1, IN2)
pwmB = setPinConfig(ENB, IN3, IN4)

def angle_to_percent (angle) :
    if angle > 180 or angle < 0 :
        return False
    start = 4
    end = 12.5
    ratio = (end - start)/180
    angle_as_percent = angle * ratio
    return start + angle_as_percent

b=0
try:
    while True:
        print(b)
        GPIO.output(17, False)
        time.sleep(0.5)

        GPIO.output(17, True)
        time.sleep(0.000001)
        GPIO.output(17, False)

        while GPIO.input(18) == 0:
            start = time.time()

        while GPIO.input(18) == 1:
            stop = time.time()

        time_interval = stop - start
        distance = time_interval * 17000
        distance = round(distance, 2)

        print("Distance => ", distance, "cm")
        
        if distance<=40 and distance>10:
            setMotor(CH1, 0, STOP)
            setMotor(CH2, 0, STOP)  
            print("turn")
            pwm.ChangeDutyCycle(angle_to_percent(0))
            if distance<=30 and distance>10:
                print("right")
                pwm.ChangeDutyCycle(angle_to_percent(170))
                Process(setMotor(CH1, 30, BACKWORD)).start()
                Process(setMotor(CH2, 30, FORWARD)).start()
                if distance<=30 and distance>10:
                    setMotor(CH1, 30, BACKWORD)
                    setMotor(CH2, 30, BACKWORD)
            else:
                print("reft")
                Process(setMotor(CH1, 30, FORWARD)).start()
                Process(setMotor(CH2, 30, BACKWORD)).start()
                            
        elif distance<=10:
            pwm.start(angle_to_percent(90))
            print("backword")
            setMotor(CH1, 30, BACKWORD)
            setMotor(CH2, 30, BACKWORD)
            sleep(0.5)
            b=b+1
            if b>2:
                Process(setMotor(CH1, 30, BACKWORD)).start()
                Process(setMotor(CH2, 30, FORWARD)).start()
        elif distance>=900:
            pwm.start(angle_to_percent(90))
            print("error")
            setMotor(CH1, 0, STOP)
            setMotor(CH2, 0, STOP)
            b=b+1
            if b>2:
                Process(setMotor(CH1, 30, BACKWORD)).start()
                Process(setMotor(CH2, 30, FORWARD)).start()
        elif distance<=900 and distance>40:
            pwm.start(angle_to_percent(90))
            print("drive")
            setMotor(CH1, 20, FORWARD)
            setMotor(CH2, 20, FORWARD)
            b=0
        
            
        else:
            pwm.start(angle_to_percent(90))
            print("drive")
            setMotor(CH1, 20, FORWARD)
            setMotor(CH2, 20, FORWARD)
            b=0
            

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Driving End")


