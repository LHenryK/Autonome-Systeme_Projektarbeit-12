import json
import time
from modules.interfaces.ip.socket_client_handler import *

import pygame
import math

angles = []
distances = []

pygame.init()
screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
done = False

scale = 100

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)


def onUpdate(serverResponse):
    global angles, distances
    # Convert server response into readable json obj

    # Check type of server response
    try:
        serverJsonObj = json.loads(serverResponse)
        print(serverResponse)
        if(serverJsonObj['type'] == "data"):
            angles = serverJsonObj['angles']
            distances = serverJsonObj['distances']
    except:
        print("Could not read from server response!")
        return
    


if __name__ == "__main__":
    client = ClientHandler("[Hostname eintragen!]", 5050)
    client.setCallback(onUpdate)
    client.start()

    while len(angles) == 0:
        print("Waiting ...")
        time.sleep(1)

    print("Starting visualisation ...")

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        screen.fill((0, 0, 0))  # Bildschirm leeren
        pygame.draw.circle(screen, green, (400, 400), 15)  # Ursprungsmarker
        scale = 400/max(distances)

        
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

    client.disconnect()

    pygame.quit()