import serial
import math
from modules.lidar.lidar_calc import calcLidarData

class LidarConnector:
    # __init__
    # serialPort: Specify the right serial port connected with the lidar scanner
    #
    def __init__(self, serialPort: str):
        # Initilise serial connection
        self.ser = serial.Serial(port=serialPort,
                            baudrate=230400,
                            timeout=5.0,
                            bytesize=8,
                            parity='N',
                            stopbits=1)


        self.tmpString = ""
        self.angles = list()
        self.distances = list()

    def getMessurement(self) -> tuple:
        self.angles.clear()
        self.distances.clear()
        
        i = 0
        while not (i % 40 == 39):
            loopFlag = True
            flag2c = False

            while loopFlag:
                b = self.ser.read()
                
                tmpInt = int.from_bytes(b, 'big')

                # 0x54, indicating the beginning of the data packet (LD19 document)
                if (tmpInt == 0x54):
                    self.tmpString += b.hex() + " "
                    flag2c = True
                    continue

                # 0x2c: fixed value of VerLen (LD19 document)
                elif (tmpInt == 0x2c and flag2c):
                    self.tmpString += b.hex()


                    if (not len(self.tmpString[0:-5].replace(' ','')) == 90):
                        self.tmpString = ""
                        loopFlag = False
                        flag2c = False
                        continue

                    lidarData = calcLidarData(self.tmpString[0:-5])
                
                    self.angles.extend(lidarData.Angle_i)
                    self.distances.extend(lidarData.Distance_i)

                    #print(distances)

                    self.tmpString = ""
                    loopFlag = False
                else:
                    self.tmpString += b.hex()+ " "

                flag2c = False

            i += 1
        
        newAngles = []
        newDistances = []

        for i in range(len(self.angles)):
            # Convert angle to float, negate, and add pi/2 (90 degrees in radians)
            newAngles.append(math.degrees(-float(self.angles[i]) + math.pi / 2))

            # Convert distance to float and round to the nearest integer
            newDistances.append(round(float(self.distances[i])))

        # Return the two newly created lists
        return newAngles, newDistances