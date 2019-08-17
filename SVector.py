class SVector:
	x = 0
	y = 0
	
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y
	
	def add(self, v):
		if isinstance(v, SVector):
			self.x += v.x
			self.y += v.y
		return self
	
	def sub(self, v):
		if isinstance(v, SVector):
			self.x -= v.x
			self.y -= v.y
		return self
	
	def copy(self):
		return SVector(self.x, self.y)
	
	def __str__(self):
		return 'SVector[x:' + str(self.x) + ', y:' + str(self.y) + ']'

	def __hash__(self):
		return hash((self.x, self.y))

	def __eq__(self, other):
		if not isinstance(other, SVector):
			return NotImplemented
		return self.x == other.x and self.y == other.y