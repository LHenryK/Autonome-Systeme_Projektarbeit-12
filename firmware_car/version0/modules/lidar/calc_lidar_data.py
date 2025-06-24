import math

class LidarData:
    def __init__(self, FSA, LSA, CS, Speed, TimeStamp, Degree_angle, Angle_i, Distance_i):
        self.FSA = FSA
        self.LSA = LSA
        self.CS = CS
        self.Speed = Speed
        self.TimeStamp = TimeStamp
        self.Degree_angle = Degree_angle

        #self.Confidence_i = Confidence_i
        self.Angle_i = Angle_i
        self.Distance_i = Distance_i



def calcLidarData(str):
    # Clear out all spaces from string
    str = str.replace(' ', '')

    Speed = int(str[2:4] + str[0:2], 16) / 100

    FSA = float(int(str[6:8] + str[4:6], 16)) / 100

    LSA = float(int(str[-8:-6] + str[-10:-8], 16)) / 100

    TimeStamp = int(str[-4:-2] + str[-6:-4], 16)

    CS = int(str[-2:], 16)


    Confidence_i = list()
    Angle_i = list()
    Distance_i = list()
    Degree_angle = list()


    if(LSA - FSA > 0):
        angleStep = float(LSA - FSA) / 12
    else:
        angleStep = float((LSA + 360) - FSA) / 12
    
    counter = 0
    circle = lambda deg : deg - 360 if deg >= 360 else deg

    for i in range(0, 6 * 12, 6):
        # Khoảng cách, đơn vị (mm)
        Distance_i.append(int(str[8+i+2 : 8+i+4] + str[8+i : 8+i+2], 16) / 1000)
        # Intensity, cường độ ánh sáng, càng lớn tức độ tin cậy càng chính xác
        #Confidence_i.append(int(str[8+i+4 : 8+i+6], 16))
        # Góc chiếu của điểm trong packet
        Degree_angle.append(circle(angleStep * counter + FSA))
        Angle_i.append(circle(angleStep * counter + FSA) * math.pi / 180.0)
        counter += 1
    
    lidarData = LidarData(FSA, LSA, CS, Speed, TimeStamp, Degree_angle, Angle_i, Distance_i)

    return lidarData