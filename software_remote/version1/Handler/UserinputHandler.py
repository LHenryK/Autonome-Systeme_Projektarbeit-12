import threading
import asyncio
import time
import evdev
from select import select

class UserinputHandler:
    def __init__(self, inputDevicePath: str) -> None:
        self.devicePath = inputDevicePath
        self.threadList = []

        self.userinputStates = {
            "ABS_X": 0,
            "ABS_Y": 0,
            "BTN_START": 0,
            "BTN_SELECT": 0,
            "BTN_X": 0,
            "BTN_Y": 0,
            "BTN_A": 0,
            "BTN_B": 0,
            "BTN_TL": 0,
            "BTN_TR": 0
        }

        self.userinputCallbackList = {
            "ABS_X": None,
            "ABS_Y": None,
            "BTN_START": None,
            "BTN_SELECT": None,
            "BTN_X": None,
            "BTN_Y": None,
            "BTN_A": None,
            "BTN_B": None,
            "BTN_TL": None,
            "BTN_TR": None
        }

    def getEvents(self) -> list:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        deviceList = []

        for device in devices:
            deviceList.append('Path: {0}, Name: {1}, Phys: {2}'.format(device.path, device.name, device.phys))
        
        return deviceList
    
    def setInputCallbacks(self, callbackList: dict):
        for i, (k, v) in enumerate(callbackList.items()):
            self.userinputCallbackList[k] = v

    
    def createAndRunInputFetcherThreads(self) -> None:
        _keyInputFetcherThread = KeyInputFetcher('KeyInputFetcher', self.devicePath, self.inputFetcherCallbackFunc)
        _jsInputFetcherThread = JSInputFetcher('JSInputFetcher', self.devicePath, self.inputFetcherCallbackFunc)

        self.threadList.append(_keyInputFetcherThread)
        self.threadList.append(_jsInputFetcherThread)
        
        _keyInputFetcherThread.start()
        _jsInputFetcherThread.start()
    
    def inputFetcherCallbackFunc(self, key: str, value: int):
        self.userinputStates[key] = value
        # self.userinputCallbackList[key](value)


class KeyInputFetcher(threading.Thread):
    def __init__(self, name: str, inputDevicePath: str, changeCallbackFunc):
        super(KeyInputFetcher, self).__init__()
        self.name = name

        self.devicePath = inputDevicePath
        self.callbackFunc = changeCallbackFunc

    def run(self) -> None:
        loop = asyncio.new_event_loop()
        loop.create_task(self.startFetching())
        loop.run_forever()

    async def startFetching(self) -> None:
        inputDevice = evdev.InputDevice(self.devicePath)

        while True:
            select([inputDevice], [], [])
            for deviceEvent in inputDevice.read():
                if deviceEvent.type == evdev.ecodes.EV_KEY:
                    absevent = evdev.categorize(deviceEvent)
                    if evdev.ecodes.bytype[absevent.event.type][absevent.event.code] == 'BTN_START':
                        self.callbackFunc('BTN_START', int(absevent.event.value))
                        break

                    if evdev.ecodes.bytype[absevent.event.type][absevent.event.code] == 'BTN_SELECT':
                        self.callbackFunc('BTN_SELECT', int(absevent.event.value))
                        break

                    if evdev.ecodes.bytype[absevent.event.type][absevent.event.code][1] == 'BTN_X':
                        self.callbackFunc('BTN_X', int(absevent.event.value))
                        break

                    if evdev.ecodes.bytype[absevent.event.type][absevent.event.code][1] == 'BTN_Y':
                        self.callbackFunc('BTN_Y', int(absevent.event.value))
                        break

                    if evdev.ecodes.bytype[absevent.event.type][absevent.event.code][0] == 'BTN_A':
                        self.callbackFunc('BTN_A', int(absevent.event.value))
                        break

                    if evdev.ecodes.bytype[absevent.event.type][absevent.event.code][0] == 'BTN_B':
                        self.callbackFunc('BTN_B', int(absevent.event.value))
                        break

                    if evdev.ecodes.bytype[absevent.event.type][absevent.event.code] == 'BTN_TR':
                        self.callbackFunc('BTN_TL', int(absevent.event.value))
                        break
                    
                    if evdev.ecodes.bytype[absevent.event.type][absevent.event.code] == 'BTN_TL':
                        self.callbackFunc('BTN_TR', int(absevent.event.value))
                        break

class JSInputFetcher(threading.Thread):
    def __init__(self, name, inputDevicePath: str, changeCallbackFunc):
        super(JSInputFetcher, self).__init__()
        self.name = name

        self.devicePath = inputDevicePath
        self.callbackFunc = changeCallbackFunc

    def run(self) -> None:
        loop = asyncio.new_event_loop()
        loop.create_task(self.startFetching())
        loop.run_forever()

    async def startFetching(self) -> None:
        inputDevice = evdev.InputDevice(self.devicePath)

        while True:
            select([inputDevice], [], [])
            for deviceEvent in inputDevice.read():
                if deviceEvent.type == evdev.ecodes.EV_ABS:
                    absevent = evdev.categorize(deviceEvent)
                    if evdev.ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_X':
                        self.callbackFunc('ABS_X', int(absevent.event.value))
                        break

                    if evdev.ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_Y':
                        self.callbackFunc('ABS_Y', int(absevent.event.value))
                        break



# Testing

# _userinputHandlerObj = UserinputHandler('/dev/input/event5')

# for i in _userinputHandlerObj.getEvents():
#     print(i)

# _userinputHandlerObj.createAndRunInputFetcherThreads()

# while True:
#     print('\n')
#     for key, val in enumerate(_userinputHandlerObj.userinputStates.items()):
#         print('{0}: {1}'.format(key, val))

#     time.sleep(0.25)

# ---- More testing ----

# currentXValue = 1
# currentYValue = 0

# def getDeviceEvents():
#     device = InputDevice('/dev/input/event5')
#     print(device)

#     for event in device.read():
#         lock.acquire()
#         global currentXValue
#         global currentYValue
#         if event.type == ecodes.EV_ABS: 
#             absevent = categorize(event) 
#             if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_X':
#                 print(absevent.event.value)
#                 currentXValue = int(absevent.event.value)
#                 print(currentXValue)
            
#             if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_Y':
#                 print(absevent.event.value)
#                 currentYValue = int(absevent.event.value)
#                 print(currentYValue)
#         lock.release()


# def readEvents():
#     while(True):
#         lock.acquire()
#         global currentXValue
#         global currentYValue
#         if lock.locked() != False:
#             print('X: {0}'.format(str(currentXValue)))
#             print('Y: {0}'.format(str(currentYValue)))
#             print("\n")
#         lock.release()
#         time.sleep(0.25)

# myJoystickcontrol = JoystickInput()

# for i in myJoystickcontrol.getEvents():
#     print(i)


# procA = Process(target=getDeviceEvents)  # instantiating without any argument
# procB = Process(target=readEvents)  # instantiating without any argument

# procA.start()
# procB.start()

# procB.join()

# device = InputDevice('/dev/input/event5')

# while True:
#     event = device.read_one()
#     print(event)
#     # if event.type == ecodes.EV_ABS: 
#     #     absevent = categorize(event) 
#     #     if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_X':
#     #         currentXValue = int(absevent.event.value)
        
#     #     if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_Y':
#     #         currentYValue = int(absevent.event.value)
    
#     print(currentXValue)
#     print(currentYValue)