import pygame

class UIWidget:
    uiScreenSurface: pygame.Surface
    uiScreenWidth: int
    uiScreenHight: int

    def __init__(self, screen, screenSize: tuple[int]):
        self.uiScreenSurface = screen
        self.uiScreenWidth = screenSize[0]
        self.uiScreenHight = screenSize[1]

    def updateScreenSize(self, newScreenWidth: int, newScreenHight: int):
        self.uiScreenWidth = newScreenWidth
        self.uiScreenHight = newScreenHight

        self.onScreenResize()

    def onScreenResize(self):
        pass