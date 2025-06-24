import os
import json
import time
import pygame

import RPi.GPIO as GPIO

from modules.ui.widgets.statusbar import *
from modules.ui.widgets.scatterPlot import *

from modules.ui.widgets.listMenu import *
from modules.ui.widgets.progress import *
from modules.ui.pages.homePage import *



# SECTION: Userinput callback functions:
userInputJoystickUPpin = 5
userInputJoystickDOWNpin = 6
userInputJoystickLEFTpin = 13
userInputJoystickRIGHTpin = 19

userInputJoystickSELECTpin = 4

GPIO.setmode(GPIO.BCM)

GPIO.setup(userInputJoystickUPpin, GPIO.IN)
GPIO.setup(userInputJoystickDOWNpin, GPIO.IN)
GPIO.setup(userInputJoystickLEFTpin, GPIO.IN)
GPIO.setup(userInputJoystickRIGHTpin, GPIO.IN)

GPIO.setup(userInputJoystickSELECTpin, GPIO.IN)


userInputJoystickUPvar = 0
userInputJoystickDOWNvar = 0
userInputJoystickLEFTvar = 0
userInputJoystickRIGHTvar = 0

userInputJoystickSELECTvar = 0

# Following Command will darker the background by popup's and more
# surface. fill((0,0,0)) with surface. set_alpha(25)

# _userinputHandlerObj = UserinputHandler('/dev/input/event0')
# _userinputHandlerObj.createAndRunInputFetcherThreads()

sendingMovementCmd = False
btnSelectPreviousValue = 0

showCurrentPage = False

isPageFocused = False

# white color 
color = (255,255,255) 

# light shade of the button 
color_light = (170,170,170)

# dark shade of the button 
color_dark = (100,100,100) 

# initializing the constructor 
pygame.init()

# screen resolution 
windowSize = (800, 500)

# opens up a window
os.environ["DISPLAY"] = ":0"

screen = pygame.display.set_mode(windowSize, pygame.FULLSCREEN)

# stores the width of the 
# screen into a variable 
width = screen.get_width() 

# stores the height of the 
# screen into a variable 
height = screen.get_height() 

windowSize = (width, height)

# defining a font 
smallfont = pygame.font.SysFont('Corbel',35) 

# rendering a text written in 
# this font 
text = smallfont.render('quit' , True , color) 

# testMenu = listMenu("Settings", screen)

# Try to initiate the seperated pages:

# SECTION: Initiate page objects

homePage = HomePage(title="Home", screen=screen, screenContentStart=(50, 0), screenContentEnd=(screen.get_size()[0]-15, screen.get_size()[1]-50))
homePageListItem = listMenuItem("Home Page", None, homePage)


# SECTION: Initiate widget objects

# Init top statusbar
mainStatusBar = UITopStatusBar(screen=screen, screenSize=windowSize, surfaceLoc=(0, 0, windowSize[0], 35), styleRounded=True)

mainStatusBar.addStatusBarLeftItem("Network", "Connected")
mainStatusBar.addStatusBarLeftItem("Clients:", "2 Clients")


# testMenu.addMenuItem(homePageListItem)

for i in range(3):
    newListItem = listMenuItem("Test: {0}".format(i), "Subtitle of item {0}".format(i))
    # testMenu.addMenuItem(newListItem)

newListItem2 = listMenuItem("Entry")
print(newListItem2.subTitle)


# testMenu.addMenuItem(newListItem2)

# Draw ScatterPlot:

# fClientScatterPlot = UIScatterPlot((0, 50, 90, 90))



# myProgress = Progressbar("My Progress", screen, (testMenu.getWidth(), 90), 50, 9)
# myProgress.draw()

# SECTION: Add all widgets to the widget list

appWidgetList: list[UIWidget] = [
    mainStatusBar,
    # fClientScatterPlot
]

contentFont = pygame.font.SysFont('Corbel', 25)

currentSelCarId = 0


# SECTION: TCP Socket sending

host = "Hier Server IP Eintragen!"
# Hier den Richtigen Port eintragen:
port = 123456

from modules.tcp.tcp_handler import TCPHandler

def onServerCallback(msg):
    pass


_tcpHandlerObj = TCPHandler(host, port, "cert/[Client Zertifikat einfügen", "cert/[Client Key einfügen].pem", onServerCallback)

_tcpHandlerObj.start()


def sendControlToCar(msg):
    _tcpHandlerObj.sendMsg(json.dumps({"carId": currentSelCarId, "controll": msg}))




def readFromInputs():
    global userInputJoystickUPvar
    global userInputJoystickDOWNvar
    global userInputJoystickLEFTvar
    global userInputJoystickRIGHTvar
    global userInputJoystickSELECTvar

    userInputJoystickUPvar = GPIO.input(userInputJoystickUPpin)
    userInputJoystickDOWNvar = GPIO.input(userInputJoystickDOWNpin)
    userInputJoystickLEFTvar = GPIO.input(userInputJoystickLEFTpin)
    userInputJoystickRIGHTvar = GPIO.input(userInputJoystickRIGHTpin)

    userInputJoystickSELECTvar = GPIO.input(userInputJoystickSELECTpin)

    time.sleep(0.01)

def checkInputs() -> None:
    global isRemoteConnected, sendingMovementCmd

    readFromInputs()

    if userInputJoystickUPvar == 0:
        sendingMovementCmd = True
        try:
            sendControlToCar("forward")
        
        except ConnectionError:
            isRemoteConnected = False
    
    elif userInputJoystickDOWNvar == 0:
        sendingMovementCmd = True
        try:
            sendControlToCar("backward")
        
        except ConnectionError:
            isRemoteConnected = False
            
    elif userInputJoystickLEFTvar == 0:
        sendingMovementCmd = True
        try:
            sendControlToCar("left")
        
        except ConnectionError:
            isRemoteConnected = False
    
    elif userInputJoystickRIGHTvar == 0:
        sendingMovementCmd = True
        try:
            sendControlToCar("right")
        
        except ConnectionError:
            isRemoteConnected = False
    
    else:
        sendingMovementCmd = False
        try:
            sendControlToCar("stop")
        
        except ConnectionError:
            isRemoteConnected = False


if __name__=='__main__':
    # Run until the user asks to quit
    running = True
    while running:
        # if "macOS" not in platform.platform():
    
        checkInputs()

        events = pygame.event.get()

        for event in events:
            # Track state of arrow keys
            # print("Running")

            # Quit application by event
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.VIDEORESIZE:
                print(f"WindowHeight: {event.h}")
                print(f"WindowWidth: {event.w}")
                windowHeight = event.h
                windowWidth = event.w

                # Update all page objects
                homePage.updateScreenSize((50, 0), (event.w, event.h))

                # Update all widget objects
                for widget in appWidgetList:
                    widget.updateScreenSize(event.w, event.h)

                pygame.display.update()
			
            if event.type == pygame.KEYDOWN and isPageFocused == False:
                if event.key == pygame.K_DOWN:
                    ...
                    # if testMenu.currentIndex < len(testMenu.listItemList)-1:
                    #     testMenu.currentIndex += 1
                
                if event.key == pygame.K_UP:
                    ...
                    # if testMenu.currentIndex > 0:
                    #     testMenu.currentIndex -= 1

        # checkUserInput()

        # if isPageFocused == True:
        #     testMenu.isFocused = False
        # else:
        #     testMenu.isFocused = True

        # fills the screen with a color 
        screen.fill((0, 0, 0))

        # SECTION: Insert update screen functions of widgets

        mainStatusBar.draw()


        # Draw test menu:
        # if testMenu.isMenuShowed == True:
        #     testMenu.draw()

        # Show page spizific content
        # if testMenu.listItemList[testMenu.currentIndex].uiPage != None:
        #     testMenu.listItemList[testMenu.currentIndex].uiPage.draw()
        # else:
        #     contentText = contentFont.render("This is the Content: {0}".format(testMenu.listItemList[testMenu.currentIndex].title), True, (0, 0, 0))
        #     screen.blit(contentText, (2*testMenu.menuItemMargin[0]+testMenu.menuItemSize[0]+50, height/2-contentText.get_size()[1]/2))

        # myProgress.update()

        pygame.display.update()

        # # Flip the display
        # pygame.display.flip()

        pygame.time.delay(10)

    # Done! Time to quit.
    pygame.quit()
    GPIO.cleanup()