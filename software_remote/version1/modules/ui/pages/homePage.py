import pygame
from datetime import datetime

from modules.ui.pages.page import *

# white color 
color = (255,255,255) 

# light shade of the button 
color_light = (170,170,170)

# dark shade of the button 
color_dark = (100,100,100) 

class HomePage(UIPage):
    def onStart(self):
        changeNetworkSettingButton = UIPageButton(self.screen, (self.screenContentStart[0]+(self.screenContentEnd[0]-self.screenContentStart[0])/2, self.screenContentStart[1]+(self.screenContentEnd[1]-self.screenContentStart[1])/2))
        changeNetworkSettingButton.setSize(80, 30)
        changeNetworkSettingButton.backgroundColor = color_dark
        self.addContentElement(changeNetworkSettingButton)

    def onInput(self, eventType: object = None, eventInput: object = None, state: int = None) -> None:
        # if eventType is InputTypes.JOYINPUT:
        #     if eventInput is InputTypes.BTN_SELECT:

        # if eventType is InputTypes.BTNINPUT:
        pass

    def updateScreenSize(self, screenContentStart: tuple, screenContentEnd: tuple):
        super().updateScreenSize(screenContentStart, screenContentEnd)

        self.contentWidgetsList[0].updateScreenPos((self.screenContentStart[0]+(self.screenContentEnd[0]-self.screenContentStart[0])/2, self.screenContentStart[1]+(self.screenContentEnd[1]-self.screenContentStart[1])/2))
    

    def draw(self):

        # Overview of widgets
        # -> UPPER LEFT / MIDDLE CORNER: 1 or 2 lidar live scans from server
        # -> LOWER LEFT / MIDDLE CORNER: 1 lidar live control stick animation (focused car)

        # -> LOWER RIGHT CORNER: Connection informations / focuse on car / modes of cars ...

        now = datetime.now()
        clockFont = pygame.font.SysFont('Corbel', 44)
        contentText = clockFont.render('{0}:{1} Uhr'.format(str(now.hour), str(now.minute)), True, (0, 0, 0))
        self.screen.blit(
            contentText,
            (
                self.screenContentStart[0]+(self.screenContentEnd[0]-self.screenContentStart[0])/2-contentText.get_size()[0]/2,
                75
            )
        )

        for i in self.contentWidgetsList:
            i.draw()