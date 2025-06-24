import pygame

class UIPageWidget:
    def __init__(self, screen: pygame.Surface, screenPos: tuple = (None, None)) -> None:
        self.widgetName: str = None
        self.screen: pygame.Surface = screen
        self.screenPos: tuple = screenPos
        
        self.widgetSize: tuple = (50, 20)
        
        self.foregroundColor: tuple = (0, 0, 0)
        self.backgroundColor: tuple = None
        
        self.isActive = False
        
        self.onStart()

    def onStart(self) -> None:
        pass

    def draw(self) -> None:
        pass

    def updateScreenPos(self, newScreenPos) -> None:
        self.screenPos = newScreenPos

    def setSize(self, width: int, height: int) -> None:
        self.widgetSize = (width, height)

    def setBackgroundColor(self, red: int = 0, green: int = 0, blue: int = 0):
        self.backgroundColor = (red, green, blue)

    def setActive(self) -> None:
        self.isActive = True

    def setInActive(self) -> None:
        self.isActive = False

class UIPageLabel(UIPageWidget):
    def __init__(self, screen: pygame.Surface, screenPos: tuple, text: str = None, size: int = 12) -> None:
        super().__init__(screen, screenPos)
        self.labelText = text
        self.lableSize = size
        self.lableFont = 'Corbel'

    # Set diffrent parameters
    def setFont(self, textFont: str):
        self.lableFont = textFont

    def draw(self):
        labelObjFont = pygame.font.SysFont(self.lableFont, self.size)
        contentText = labelObjFont.render(self.labelText, True, self.foregroundColor)
        self.screen.blit(contentText, (self.screenContentStart[0]+(self.screenContentEnd[0]-self.screenContentStart[0])/2-contentText.get_size()[0]/2, self.screenContentStart[1]+(self.screenContentEnd[1]-self.screenContentStart[1])/2-contentText.get_size()[1]/2))


class UIPageButton(UIPageWidget):
    def draw(self):
        cornerRadius = 15
        polyBackgroundArr = [
            (self.screenPos[0]+cornerRadius, self.screenPos[1]),
            (self.screenPos[0]+self.widgetSize[0]-cornerRadius, self.screenPos[1]),
            (self.screenPos[0]+self.widgetSize[0], self.screenPos[1]+cornerRadius),
            (self.screenPos[0]+self.widgetSize[0], self.screenPos[1]+self.widgetSize[1]-cornerRadius),
            (self.screenPos[0]+self.widgetSize[0]-cornerRadius, self.screenPos[1]+self.widgetSize[1]),
            (self.screenPos[0]+cornerRadius, self.screenPos[1]+self.widgetSize[1]),
            (self.screenPos[0], self.screenPos[1]+self.widgetSize[1]-cornerRadius),
            (self.screenPos[0], self.screenPos[1]+cornerRadius),
        ]
        pygame.draw.polygon(self.screen, self.backgroundColor, polyBackgroundArr)
        pygame.draw.circle(self.screen, self.backgroundColor, (round(self.screenPos[0]+cornerRadius), round(self.screenPos[1]+cornerRadius)), cornerRadius)
        pygame.draw.circle(self.screen, self.backgroundColor, (round(self.screenPos[0]+self.widgetSize[0]-cornerRadius), round(self.screenPos[1]+cornerRadius)), cornerRadius)
        pygame.draw.circle(self.screen, self.backgroundColor, (round(self.screenPos[0]+self.widgetSize[0]-cornerRadius), round(self.screenPos[1]+self.widgetSize[1]-cornerRadius)), cornerRadius)
        pygame.draw.circle(self.screen, self.backgroundColor, (round(self.screenPos[0]+cornerRadius), round(self.screenPos[1]+self.widgetSize[1]-cornerRadius)), cornerRadius)

class UIPageEntry(UIPageWidget):
    def draw(self):
        pass

# Outscource this class into a type file !!!
class InputTypes:
    JOYINPUT: type = None
    BTNINPUT: type = None

    BTN_START: type = None
    BTN_SELECT: type = None
    BTN_X: type = None
    BTN_Y: type = None
    BTN_A: type = None
    BTN_B: type = None
    BTN_TL: type = None
    BTN_TR: type = None

class UIPage:
    def __init__(self, title: str = None, screen: pygame.Surface = None, screenContentStart: tuple = (50, 0), screenContentEnd: tuple = (None, None)) -> None:
        self.title = title
        self.screen: pygame.Surface = screen
        self.screenContentStart = screenContentStart
        self.screenContentEnd = screenContentEnd

        self.currentIndex = 0
        self.contentWidgetsList: list[UIPageWidget] = []

        self.onStart()
    
    def onStart(self):
        pass

    def onInput(self, eventType: type = None, state: int = None) -> None:
        pass

    def updateScreenSize(self, screenContentStart: tuple, screenContentEnd: tuple):
        self.screenContentStart = screenContentStart
        self.screenContentEnd = screenContentEnd

    def draw(self) -> None:
        print("Test")

    def addContentElement(self, newUIPageWidget: UIPageWidget) -> None:
        self.contentWidgetsList.append(newUIPageWidget)