from pygame import Surface

from modules.ui.widgets.widget import *

# SECTION: Working convertion:

'''
takeMeasurements()
# scale = 400/max(distances)


for i in range(len(angles)):
    # Winkel in Bogenmaß
    angle_rad = -float(angles[i]) + math.pi / 2
    distance = round(float(distances[i]) * scale)

    # x- und y-Koordinaten berechnen
    x = 400 + int(distance * math.cos(angle_rad))
    y = 400 - int(distance * math.sin(angle_rad))  # Beachte Achsenumkehr

    # Punkt zeichnen
    pygame.draw.circle(screen, blue, (x, y), 2)
'''


class UIScatterPlot(UIWidget):
    plotData: tuple

    def __init__(self, screen: Surface, screenSize: tuple[int]):
        super().__init__(screen=screen, screenSize=screenSize)

    
    def updatePlotData(self, newAngles: float, newDistances: float):
        self.plotData = (newAngles, newDistances)
    
    def draw(self):
        try:
            assert(self.plotData)

        except:
            # Draw on Screen 'No Data Avalible!'
            print("No Data avalible!")