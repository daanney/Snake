from random import randint
from SConfig import SConfig
from SVector import SVector

class Apple:
	
	def __init__(self):
		self.reset()
		
	def getPosition(self):
		return self.position
		
	def reset(self):
		self.position = SVector(randint(1, SConfig.size - 2), randint(1, SConfig.size - 2))
		self.isReset = True
		return self.getPosition()
		
	def _drawinit(self, board):
		# x1:y1 = top-left corner; x2:y2 = bottom-right corner
		x = self.position.x * SConfig.px
		y = self.position.y * SConfig.px
		self.uiApple = board.create_rectangle(x, y, x + SConfig.px, y + SConfig.px, 
			fill='red', outline='white', width=1)
		
	def _draw(self, board):
		if not self.isReset: return
		x = self.position.x * SConfig.px
		y = self.position.y * SConfig.px
		board.coords(self.uiApple, x, y, x + SConfig.px, y + SConfig.px)
		self.isReset = False

	def _drawstop(self, board):
		pass
		
	def __draw(self):
		fill(255, 0, 0)
		rect(self.position.x * SConfig.px, self.position.y * SConfig.px, SConfig.px, SConfig.px)
