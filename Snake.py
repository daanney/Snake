from operator import add 
from collections import deque
from SConfig import SConfig
from SVector import SVector

class Snake:
	body = []
	alive = True

	directions = { 
		 'UP':   SVector(0, -1)
		,'RIGHT': SVector(1, 0)
		,'DOWN':  SVector(0, 1)
		,'LEFT':  SVector(-1, 0)
		,'NOCHANGE': SVector(0, 0)
	}

	position  = None
	direction = None
	directKey = None
	
	def __init__(self, _length = 3, _position = SVector(0, 0), _direction = 'RIGHT'):
		self.setDirection(_direction)
		self.position = _position
		self.body = deque([])
		self.uiBody = deque([])
		self.alive = True
		self.died = False

		for i in range(_length): self.move(grow = True)
	
	def getNextPosition(self, for_direction=None):
		direction = for_direction if for_direction != None else self.direction
		if not isinstance(direction, SVector): direction = self.directions.get(direction)
		return self.position.copy().add(direction)

	def getPosition(self):
		return self.position
	
	def isAtPosition(self, position):
		return position in self.body

	def willDie(self, nextPosition):
		return (self.isAtPosition(nextPosition)
			or not(0 <= nextPosition.x < SConfig.size)
			or not(0 <= nextPosition.y < SConfig.size))

	def isDirectionFree(self, directionKey):
		v = self.directions.get(directionKey, False)
		if False == v: return 0
		return 0 if self.willDie( self.position.copy().add(v) ) else 1
	
	def move(self, grow = False):
		if not grow: self.body.popleft()
		self.hasGrown = grow
		self.position = self.getNextPosition()
		self.body.append(self.position)
		
	def setDirection(self, directionKey):
		if self.newDirectionAllowed(directionKey): 
			self.direction = self.directions.get(directionKey)
			self.directKey = directionKey

	def newDirectionAllowed(self, directionKey):
		v = self.directions.get(directionKey, False)
		return (False != v # exists
			and self.direction != v # is not current
			and self.directions.get('NOCHANGE') != v.copy().add(self.direction)) # has change

	def getDirectionKey(self):
		return self.directKey
	
	def die(self):
		self.alive = False
		self.died = True
		
	def _drawinit(self, board):
		for v in self.body:
			x = v.x * SConfig.px
			y = v.y * SConfig.px
			bodyPart = board.create_rectangle(x, y, x + SConfig.px, y + SConfig.px,
				fill='#000', outline='white', width=1)
			self.uiBody.append(bodyPart)
			self.uiHead = bodyPart
			
		# Head
		board.itemconfig(self.uiHead, fill='#b45050')
		self.hasGrown = False
		
	def _draw(self, board):
		# set current head to black
		board.itemconfig(self.uiHead, fill='#000')

		x = self.position.x * SConfig.px
		y = self.position.y * SConfig.px

		if self.hasGrown:
			# create new element as head
			self.uiHead = board.create_rectangle(x, y, x + SConfig.px, y + SConfig.px,
				fill='#b45050', outline='white', width=1)
			self.hasGrown = False
		else:
			# rearrange tip of tail as head
			self.uiHead = self.uiBody.popleft()
			board.itemconfig(self.uiHead, fill='#b45050')
			board.coords(self.uiHead, x, y, x + SConfig.px, y + SConfig.px)

		self.uiBody.append(self.uiHead)

	def _drawstop(self, board):
		if self.died:
			for bodyPart in self.uiBody: board.itemconfig(bodyPart, fill='#b45050')
			self.died = False
		
		

		'''
		for v in self.body[0:-1]:
			x = v.x * SConfig.px
			y = v.y * SConfig.px
			board.create_rectangle(x, y, x + SConfig.px, y + SConfig.px,
				fill='#000', outline='white', width=1)
			
		# Head
		head = self.body[-1]
		x = head.x * SConfig.px
		y = head.y * SConfig.px
		board.create_rectangle(x, y, x + SConfig.px, y + SConfig.px,
			fill='#b45050', outline='white', width=1)
		'''


''' 
old, was for Processing ...
	def _draw(self):
		# Body
		
		if self.alive: fill(0)
		else: fill(180, 80, 80)
		
		for v in self.body:
			stroke(255)
			rect(v.x * SConfig.px, v.y * SConfig.px, SConfig.px, SConfig.px)
			
		# Head 
		stroke(255)
		fill(180, 80, 80)
		rect(v.x * SConfig.px, v.y * SConfig.px, SConfig.px, SConfig.px)
		self.body[-1]
'''