from modules.lidar.lidar_handler import LidarConnector

import pygame
import math

lc = LidarConnector("/dev/tty.usbserial-0001")

angles = []
distances = []

pygame.init()
screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
done = False

scale = 300

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

def takeMeasurements():
    global angles, distances

    angles, distances = lc.getMessurement()



if __name__ == "__main__":
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        screen.fill((0, 0, 0))  # Bildschirm leeren
        pygame.draw.circle(screen, green, (400, 400), 15)  # Ursprungsmarker
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

        pygame.display.update()  # Bildschirm aktualisieren

    pygame.quit()