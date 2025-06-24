from modules.ui.pages.page import UIPage
import pygame

class Progressbar:
    def __init__(self, title: str, screen, place: tuple, width: int, hight: int) -> None:
        self.currentIndex: int = 0
        self.screen: pygame.Surface = screen
        self.progWidth = width
        self.progHight = hight
        self.startCoordinates = place
        self.endCoordinates = (place[0]+width, place[1]+hight)
        self.isFocused = True
        self.menuTitleFont = pygame.font.SysFont('Corbel', 18)
        self.progressValue = 0
        self.modeMath = 'increase'

    def update(self):
        if self.modeMath == 'increase' and 0 <= self.progressValue < 100:
            self.progressValue += 1
        elif self.modeMath == 'decrease' and 0 < self.progressValue <= 100:
            self.progressValue -= 1
        elif self.progressValue > 99:
            self.modeMath = 'decrease'
        elif self.progressValue < 1:
            self.modeMath = 'increase'
        
        self.draw()

    def draw(self):
        pygame.draw.rect(self.screen, (0, 0, 0), (self.startCoordinates[0], self.startCoordinates[1], self.endCoordinates[0], self.endCoordinates[1]), border_radius=10)

        pygame.draw.circle(self.screen, (255, 255,255), (self.startCoordinates[0]+2+(self.endCoordinates[0]-self.startCoordinates[1]-4)*self.progressValue/100, self.startCoordinates[1]), 5)

        pygame.draw.rect(self.screen, (0, 255, 0), (self.startCoordinates[0]+2, self.startCoordinates[1]+2, self.startCoordinates[0]+2+(self.endCoordinates[0]-self.startCoordinates[1]-4)*self.progressValue/100, self.endCoordinates[1]-4), border_radius=10)

