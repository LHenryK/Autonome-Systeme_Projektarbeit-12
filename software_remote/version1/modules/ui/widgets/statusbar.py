from datetime import datetime
import random
import pygame

from modules.ui.widgets.widget import *


# SECTION: UIStatusBar

class UIStatusBar(UIWidget):
    statusBarDefaultBorderRadius: int = 5
    statusBarDefaultBorderPadding: int = 5
    statusBarDefaultBorderItemPadding: int = 0
    statusBarDefaultBgColors: list[tuple[int]] = [
        (255, 255, 255),
        (0, 0, 0)
    ]

    statusBarSurfaceLoc: tuple
    statusBarSurfaceHight: int = 35

    statusBarItemLeftSurfaceLoc: tuple
    statusBarItemRightSurfaceLoc: tuple

    statusBarItemListLeft: list[object] = []
    statusBarItemListRight: list[object] = []
    statusBarSysClockItem: object
    
    def __init__(self, screen: pygame.Surface, screenSize: tuple[int], surfaceLoc: tuple, styleRounded: bool = False):
        super().__init__(screen=screen, screenSize=screenSize)
        print(surfaceLoc)
        self.statusBarDefaultHight = surfaceLoc[3]
        self.statusBarSurfaceLoc = surfaceLoc
        self.statusBarStyleRounded = styleRounded

        self.onScreenResize()
        self.initilise()
    
    def initilise(self):
        newClockItemLock = (
            self.statusBarSurfaceLoc[2]/3,
            self.statusBarSurfaceLoc[1],
            self.statusBarSurfaceLoc[2]/3*2,
            self.statusBarSurfaceLoc[3]
        )
        print(newClockItemLock)
        self.statusBarSysClockItem = UIStatusItemSysClock(self.uiScreenSurface, newClockItemLock)

        # Add 
    def addStatusBarLeftItem(self, itemName: str, itemValue: str) -> None:
        print(self.statusBarSurfaceLoc)

        listLen = len(self.statusBarItemListLeft)
        print(listLen)

        print(self.statusBarItemLeftSurfaceLoc)
        newLeftStatusBarItem = UIStatusItem(
            self.uiScreenSurface, 
            (self.statusBarItemLeftSurfaceLoc[0], 
             self.statusBarItemLeftSurfaceLoc[1], 
             self.statusBarItemLeftSurfaceLoc[2], 
             self.statusBarItemLeftSurfaceLoc[3]),
            itemName,
            itemValue
        )
        
        self.statusBarItemListLeft.append(newLeftStatusBarItem)
        self.updateItemListLeftElements()

    def updateItemListLeftElements(self):
        listLen = len(self.statusBarItemListLeft)

        statusBarLeftLocWidth = self.statusBarItemLeftSurfaceLoc[2]-self.statusBarItemLeftSurfaceLoc[0]
        singleStatusBarItemWidth = statusBarLeftLocWidth/(listLen)

        print(listLen)
        print(singleStatusBarItemWidth)

        for ind, i in enumerate(self.statusBarItemListLeft):
            i.updateSurfaceLoc((
                self.statusBarItemLeftSurfaceLoc[0]+singleStatusBarItemWidth*ind,
                self.statusBarItemLeftSurfaceLoc[1],
                self.statusBarItemLeftSurfaceLoc[0]+singleStatusBarItemWidth*ind+singleStatusBarItemWidth,
                self.statusBarItemLeftSurfaceLoc[3]
            ))

    def onScreenResize(self):
        print(self.statusBarSurfaceLoc[3])
        self.statusBarSurfaceLoc = (0, 0, self.uiScreenWidth, self.statusBarDefaultHight)

        if self.statusBarStyleRounded == True:
            self.statusBarBorderRadius = self.statusBarDefaultBorderRadius
            
        else:
            self.statusBarBorderRadius = -1
        
        self.statusBarSurfaceLoc = (
            self.statusBarSurfaceLoc[0]+self.statusBarDefaultBorderPadding,
            self.statusBarSurfaceLoc[1]+self.statusBarDefaultBorderPadding,
            self.statusBarSurfaceLoc[2]-2*self.statusBarDefaultBorderPadding,
            self.statusBarSurfaceLoc[3]-2*self.statusBarDefaultBorderPadding
        )

        self.statusBarItemLeftSurfaceLoc = (
            self.statusBarSurfaceLoc[0],
            self.statusBarSurfaceLoc[1],
            self.statusBarSurfaceLoc[0]+(self.statusBarSurfaceLoc[2]-self.statusBarSurfaceLoc[0])/3,
            self.statusBarSurfaceLoc[3]
        )

        self.statusBarItemRightSurfaceLoc = (
            self.statusBarSurfaceLoc[0]/3,
            self.statusBarSurfaceLoc[1],
            self.statusBarSurfaceLoc[2]+(self.statusBarSurfaceLoc[2]-self.statusBarSurfaceLoc[0]),
            self.statusBarSurfaceLoc[3]
        )
    
    def update(self):
        
        # Draw background
        pygame.draw.rect(surface=self.uiScreenSurface, color=self.statusBarDefaultBgColors[0], rect=self.statusBarSurfaceLoc, border_radius=self.statusBarBorderRadius)

        for i in self.statusBarItemListLeft:
            i.draw()

        self.statusBarSysClockItem.draw()
        
    
    def draw(self):
        self.update()

# SECTION: UIStatusBarItem

class UITopStatusBar(UIStatusBar):
    def __init__(self, screen: pygame.Surface, screenSize: tuple[int], surfaceLoc: tuple, styleRounded: bool):
        super().__init__(screen=screen, screenSize=screenSize, surfaceLoc=surfaceLoc, styleRounded=styleRounded)
        self.statusBarItems = []
        self.onScreenResize()

class UIStatusItem:
    statusItemIsEnabled = True

    statusItemDefaultBorderRadius = 2
    statusItemDefaultBorderPadding = 2

    statusItemDefaultTitleFontSize = 14
    statusItemDefaultTitleFontFamily = 'Verdana'
    
    statusItemDefaultColorSelection = 1
    statusItemDefaultBgColor = [
        (200, 200, 200),
        (0, 0, 0)
    ]
    statusItemDefaultFgColor = [
        (0, 0, 0),
        (200, 200, 200)
    ]

    statusItemName: str
    statusItemValue: str

    def __init__(self, screen: pygame.surface.Surface, surfaceLoc: tuple, name: str, value):
        self.statusItemSurface = screen
        self.statusItemName = name
        self.statusItemValue = value

        self.updateSurfaceLoc(surfaceLoc)
        self.statusItemDefaultTitleFont = pygame.font.SysFont(self.statusItemDefaultTitleFontFamily, self.statusItemDefaultTitleFontSize)

    def updateSurfaceLoc(self, newSurfaceLoc):
        # print(newSurfaceLoc)
        self.statusItemSurfaceLoc = (
            newSurfaceLoc[0]+self.statusItemDefaultBorderPadding,
            newSurfaceLoc[1]+self.statusItemDefaultBorderPadding,
            newSurfaceLoc[2]-2*self.statusItemDefaultBorderPadding,
            newSurfaceLoc[3]-2*self.statusItemDefaultBorderPadding
        )

    def update(self):
        # print(self.statusItemSurfaceLoc[2])
        pygame.draw.rect(surface=self.statusItemSurface, color=self.statusItemDefaultBgColor[self.statusItemDefaultColorSelection], rect=(self.statusItemSurfaceLoc[0], self.statusItemSurfaceLoc[1], self.statusItemSurfaceLoc[2]-self.statusItemSurfaceLoc[0], self.statusItemSurfaceLoc[3]), border_radius=self.statusItemDefaultBorderRadius)

        # # Showing Text in Box
        statusItemTitleRender = self.statusItemDefaultTitleFont.render(self.statusItemValue, True, self.statusItemDefaultFgColor[self.statusItemDefaultColorSelection])
        self.statusItemSurface.blit(
            statusItemTitleRender, 
            (
                self.statusItemSurfaceLoc[0]+(self.statusItemSurfaceLoc[2]-self.statusItemSurfaceLoc[0])/2-statusItemTitleRender.get_width()/2,
                self.statusItemSurfaceLoc[1]+3+(self.statusItemSurfaceLoc[3]-self.statusItemSurfaceLoc[1])/2-statusItemTitleRender.get_height()/2
            )
        )

    def draw(self):
        self.update()

class UIStatusItemSysClock(UIStatusItem):
    def __init__(self, screen: pygame.surface.Surface, surfaceLoc: tuple):
        super().__init__(screen=screen, surfaceLoc=surfaceLoc, name="Clock", value="Clock")
    
    def update(self):
        pygame.draw.rect(surface=self.statusItemSurface, color=self.statusItemDefaultBgColor[self.statusItemDefaultColorSelection], rect=(self.statusItemSurfaceLoc[0], self.statusItemSurfaceLoc[1], self.statusItemSurfaceLoc[2]-self.statusItemSurfaceLoc[0], self.statusItemSurfaceLoc[3]), border_radius=self.statusItemDefaultBorderRadius)

    def draw(self):
        if self.statusItemIsEnabled:
            self.update()

            now = datetime.now()
            clockFont = pygame.font.SysFont(self.statusItemDefaultTitleFontFamily, self.statusItemDefaultTitleFontSize)
            statusClock = clockFont.render(datetime.now().strftime("%H:%M")+' Uhr', True, self.statusItemDefaultFgColor[self.statusItemDefaultColorSelection])
            self.statusItemSurface.blit(
                statusClock,
                ((self.statusItemSurfaceLoc[0]+(self.statusItemSurfaceLoc[2]-self.statusItemSurfaceLoc[0])/2)-statusClock.get_width()/2, self.statusItemSurfaceLoc[1]+(self.statusItemSurfaceLoc[3]+4-self.statusItemSurfaceLoc[1])/2-clockFont.get_height()/2)
            )
