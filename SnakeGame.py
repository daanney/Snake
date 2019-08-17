from Apple import Apple
from Snake import Snake
from SConfig import SConfig

class SnakeGame:
	
	def __init__(self, board=None, autostart=False):
		self.board = board
		self.restart(autostart)
	
	def restart(self, autostart=False):
		self.score = 0
		self.snake = Snake()
		self.apple = Apple()
		self.stopped = not autostart # game not running (no steps made)
		self.finished = False # game is done and can't be resumed
		self.didRestart = True
		self.speed = SConfig.speed
		self.uiInstrText = 'press <SPACE> to start'
		
	def nextMove(self):
		if self.stopped: return
		
		# check if it's gonna hit..
		nextPosition = self.snake.getNextPosition()
		willEatApple = nextPosition == self.apple.getPosition()
		
		if self.snake.willDie(nextPosition):
			print('+------------+')
			print('| Snake died |')
			print('+------------+')
			print(nextPosition)
			self.stop()
			return
		
		self.snake.move(willEatApple)

		if willEatApple:
			while self.snake.isAtPosition(self.apple.reset()): pass
			self.score += 1
			self.speed -= SConfig.speedIncrease
			if self.speed < 0: self.speed = 0
			print(self.score)
			print(self.apple.getPosition())
	
	def setDirection(self, direction):
		if not self.stopped: self.snake.setDirection(direction)
	
	def stop(self):
		self.snake.die()
		self.finished = self.stopped = True
		self.uiInstrText = 'press <R> to restart'
	
	def isFinished(self):
		return self.finished

	def getScore(self):
		return self.score

	def getBoardSize(self):
		return SConfig.size
	
	def pause(self):
		if self.isFinished(): 
			self.stopped = True
			return
		
		self.stopped = not self.stopped
		self.uiInstrText = 'press <SPACE> to start'
	
	def _drawinit(self):
		self.snake._drawinit(self.board)
		self.apple._drawinit(self.board)

		self.uiScore = self.board.create_text(SConfig.px, SConfig.size * SConfig.px - SConfig.px, 
			text='Score: ' + str(self.score), 
			fill='grey', font='Verdana 24', anchor='sw')

		#self.uiInstrText = 'Press <SPACE> to start' if not self.finished else 'Press <R> to restart'
		pos = (SConfig.size / 2) * SConfig.px
		self.uiInstr = self.board.create_text(pos, pos, text=self.uiInstrText, fill='red', font='Verdana 30', 
			state='normal' if self.stopped else 'hidden')

	def _draw(self):
		if self.didRestart:
			self.board.delete('all')
			self._drawinit()
			self.didRestart = False
			return

		if self.stopped: 
			self._drawstop()
			return

		self.snake._draw(self.board)
		self.apple._draw(self.board)
		self.board.itemconfig(self.uiScore, text='Score: ' + str(self.score))
		self.board.itemconfig(self.uiInstr, text=self.uiInstrText, state='hidden')

	def _drawstop(self):
		self.snake._drawstop(self.board)
		self.apple._drawstop(self.board)
		self.board.tag_raise(self.uiInstr, self.uiScore)
		self.board.itemconfig(self.uiScore, text='Score: ' + str(self.score))
		self.board.itemconfig(self.uiInstr, text=self.uiInstrText, state='normal')

	def __draw(self):
		self.snake.__draw()
		self.apple.__draw()
		fill(180)
		textFont(createFont("Verdana", 24))
		text('Score: ' + str(self.score), 10, SConfig.size * SConfig.px - 10)
