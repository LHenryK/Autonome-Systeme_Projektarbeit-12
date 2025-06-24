import json
from datetime import datetime
from threading import Thread

import time

import RPi.GPIO as GPIO

from modules.tcp.tcp_handler import TCPHandler
from modules.lidar.lidar_handler import LidarConnector

host = "Hier Server IP Eintragen!"
# Hier den Richtigen Port eintragen:
port = 123456

gpioMotorPins = (17, 18, 22, 23)
gpioPwmPins = (5, 6)
pwmDuty = 75

carId = 0

canDriveFoward = True
canDriveBackward = True

def setupGpioPins():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for i in gpioMotorPins:
        GPIO.setup(i, GPIO.OUT)

    for i in gpioPwmPins:
        GPIO.setup(i, GPIO.OUT)
    
    for i in gpioPwmPins:
        newPwmPin = GPIO.PWM(i, 100)
        newPwmPin.start(pwmDuty)
    
    time.sleep(1)

    GPIO.output(gpioMotorPins[0], GPIO.LOW)
    GPIO.output(gpioMotorPins[1], GPIO.LOW)
    GPIO.output(gpioMotorPins[2], GPIO.LOW)
    GPIO.output(gpioMotorPins[3], GPIO.LOW)

lastConTime = None
isActiveMoving = False

def moveForward():
    global isActiveMoving
    print("Run 5")
    if canDriveFoward:
        print("Run 6")
        isActiveMoving = True
        GPIO.output(gpioMotorPins[0], GPIO.HIGH)
        GPIO.output(gpioMotorPins[2], GPIO.HIGH)
        

def moveBackward():
    global isActiveMoving
    if canDriveBackward:
        isActiveMoving = True
        GPIO.output(gpioMotorPins[1], GPIO.HIGH)
        GPIO.output(gpioMotorPins[3], GPIO.HIGH)
        

def moveLeft():
    global isActiveMoving
    isActiveMoving = True
    GPIO.output(gpioMotorPins[1], GPIO.HIGH)
    GPIO.output(gpioMotorPins[2], GPIO.HIGH)
    

def moveRight():
    global isActiveMoving
    isActiveMoving = True
    GPIO.output(gpioMotorPins[0], GPIO.HIGH)
    GPIO.output(gpioMotorPins[3], GPIO.HIGH)
    

def stopMovement():
    global isActiveMoving
    isActiveMoving = False
    GPIO.output(gpioMotorPins[0], GPIO.LOW)
    GPIO.output(gpioMotorPins[1], GPIO.LOW)
    GPIO.output(gpioMotorPins[2], GPIO.LOW)
    GPIO.output(gpioMotorPins[3], GPIO.LOW)
    

def onServerMsgReceve(recvMsg):
    global lastConTime
    jsonObj = json.loads(recvMsg)

    print(recvMsg)

    if jsonObj.get('carId') == None:
        return

    print("Run1")

    if jsonObj.get('carId') != carId:
        return

    print("Run2")

    if jsonObj.get('controll') != None:
        lastConTime = datetime.now()
        print("Run3")
        match jsonObj.get('controll'):
            case "forward":
                print("Run 4")
                moveForward()
            case "backward":
                moveBackward()
            case "left":
                moveLeft()
            case "right":
                moveRight()
            case "stop":
                stopMovement()
            case _:
                pass

def checkConCmd():
    global lastConTime, isActiveMoving

    while(True):
        if isActiveMoving:
            currentTime = datetime.now()
            timeDiff = datetime.strptime(currentTime, "%H:%M:%S") - datetime.strptime(lastConTime, "%H:%M:%S")

            if timeDiff.total_seconds() > 3.0:
                stopMovement()
        time.sleep(1.5)

def angle_in_range(angle, start, end):
    angle = angle % 360
    start = start % 360
    end = end % 360
    
    if start <= end:
        return start <= angle <= end
    else:
        # Bereich über 0°-Grenze (z.B. 350° bis 10°)
        return angle >= start or angle <= end


lowerAngleVorn = 315
upperAngleVorn = 45

lowerAngleHint = 135
upperAngleHint = 225

if __name__=='__main__':
    setupGpioPins()

    _tcpHandler = TCPHandler(host, port, "cert/[Client Zertifikat einfügen]", "cert/[Client Key einfügen].pem", onServerMsgReceve)
    _tcpHandler.start()
    
    _lidarHandler = LidarConnector('/dev/ttyUSB0')

    threadCon = Thread(target=checkConCmd)
    threadCon.start()

    while(True):
        angles, distances = _lidarHandler.getMessurement()

        for angleInd, angleVal in enumerate(angles):
            if angle_in_range(angleVal, lowerAngleVorn, upperAngleVorn):
                if distances[angleInd]*100 < 20:
                    canDriveBackward = False
                    stopMovement()
                    break
                else:
                    canDriveBackward = True
            if angle_in_range(angleVal, lowerAngleHint, upperAngleHint):
                if distances[angleInd]*100 < 20:
                    canDriveFoward = False
                    stopMovement()
                    break
                else:
                    canDriveFoward = True