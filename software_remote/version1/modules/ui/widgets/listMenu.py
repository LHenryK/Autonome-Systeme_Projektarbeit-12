from modules.ui.pages.page import UIPage
import pygame

# white color 
color = (255,255,255) 

# light shade of the button 
color_light = (170,170,170) 

# dark shade of the button 
color_dark = (100,100,100) 

class listMenuItem:
	def __init__(self, title: str, subTitle: str = None, uiPage: UIPage = None) -> None:
		try:
			assert(len(title)<11)
		except:
			title = "Undefined"
		try:
			if subTitle != None:
				assert(len(subTitle)<19)
		except:
			subTitle = "Undefined"
		
		self.id = 0
		self.title: str = title
		self.subTitle: str = subTitle
		self.uiPage = uiPage

class listMenu:
	def __init__(self, title: str, screen) -> None:
		self.currentIndex: int = 0
		self.listItemList: list[listMenuItem] = []
		self.screen: pygame.Surface = screen
		self.isFocused = True
		self.menuTitleFont = pygame.font.SysFont('Corbel', 36)
		self.menuItemTitleFont = pygame.font.SysFont('Corbel', 28)
		self.menuItemSmallFont = pygame.font.SysFont('Corbel', 18)

		self.menuItemMargin: tuple = (15, 5)
		self.menuItemSize: tuple = (160, 50)
		
		self.isMenuShowed = True
		
		try:
			if title != None:
				assert(len(title) < 13)
				self.menuItemMargin = (15, 5+50)
		except:
			title = "Undefined"
		
		self.title = title

	def getWidth(self) -> int:
		return self.menuItemMargin[0] + self.menuItemSize[0]

	def addMenuItem(self, menuItemObj: listMenuItem) -> None:
		if len(self.listItemList) < 7:
			self.listItemList.append(menuItemObj)

	def draw(self) -> None:
		pygame.draw.rect(self.screen, (100, 100, 100), [0, 0, 2*self.menuItemMargin[0]+self.menuItemSize[0], self.screen.get_size()[1]])

		if self.title != None:
			titleText = self.menuTitleFont.render(self.title, True, color)
			self.screen.blit(titleText, ((2*self.menuItemMargin[0]+self.menuItemSize[0])/2-titleText.get_size()[0]/2, self.menuItemMargin[1]/2-titleText.get_size()[1]/2))

		polyArrowSize = (20, 20)
		polyArrowMarginRight = 10
		arrowThickness = 10

		for k, v in enumerate(self.listItemList):
			if k == self.currentIndex:
				rightArrowPoly = [
					[self.menuItemMargin[0]+self.menuItemSize[0]-polyArrowMarginRight-polyArrowSize[0], self.menuItemMargin[1]+k*self.menuItemSize[1]+self.menuItemSize[1]/2-polyArrowSize[1]],
					[self.menuItemMargin[0]+self.menuItemSize[0]-polyArrowMarginRight, self.menuItemMargin[1]+k*self.menuItemSize[1]+self.menuItemSize[1]/2],
					[self.menuItemMargin[0]+self.menuItemSize[0]-polyArrowMarginRight-polyArrowSize[0], self.menuItemMargin[1]+k*self.menuItemSize[1]+self.menuItemSize[1]/2+polyArrowSize[1]],
					[self.menuItemMargin[0]+self.menuItemSize[0]-polyArrowMarginRight-polyArrowSize[0], self.menuItemMargin[1]+k*self.menuItemSize[1]+self.menuItemSize[1]/2+polyArrowSize[1]-arrowThickness],
					[self.menuItemMargin[0]+self.menuItemSize[0]-polyArrowMarginRight-arrowThickness, self.menuItemMargin[1]+k*self.menuItemSize[1]+self.menuItemSize[1]/2],
					[self.menuItemMargin[0]+self.menuItemSize[0]-polyArrowMarginRight-polyArrowSize[0], self.menuItemMargin[1]+k*self.menuItemSize[1]+self.menuItemSize[1]/2-polyArrowSize[1]+arrowThickness],
				]
				
				# Highlight the background
				pygame.draw.rect(self.screen, (170, 170, 170), [0, self.menuItemMargin[1]+k*self.menuItemSize[1], 2*self.menuItemMargin[0]+self.menuItemSize[0], self.menuItemSize[1]])
				
				# Add right arrow for selection if focused !
				if self.isFocused == True:
					pygame.draw.polygon(self.screen, color, rightArrowPoly)
			
			pygame.draw.line(self.screen, color, (self.menuItemMargin[0]-10, self.menuItemMargin[1]+k*self.menuItemSize[1]), (self.menuItemMargin[0]+self.menuItemSize[0]+10, self.menuItemMargin[1]+k*self.menuItemSize[1]))
			pygame.draw.line(self.screen, color, (self.menuItemMargin[0]-10, self.menuItemMargin[1]+k*self.menuItemSize[1]+self.menuItemSize[1]), (self.menuItemMargin[0]+self.menuItemSize[0]+10, self.menuItemMargin[1]+k*self.menuItemSize[1]+self.menuItemSize[1]))
			
			newMenuItemText = self.menuItemTitleFont.render('{0}'.format(v.title), True , color)
			if v.subTitle == None:
				self.screen.blit(newMenuItemText, (self.menuItemMargin[0]+10, self.menuItemMargin[1]+k*self.menuItemSize[1]+self.menuItemSize[1]/2-newMenuItemText.get_size()[1]/2))
			
			else:
				newMenuItemSubText = self.menuItemSmallFont.render('{0}'.format(v.subTitle), True , color)
				self.screen.blit(newMenuItemText, (self.menuItemMargin[0]+10, self.menuItemMargin[1]+k*self.menuItemSize[1]+5))
				self.screen.blit(newMenuItemSubText, (self.menuItemMargin[0]+20, self.menuItemMargin[1]+k*self.menuItemSize[1]+self.menuItemSize[1]-newMenuItemSubText.get_size()[1]-5))
