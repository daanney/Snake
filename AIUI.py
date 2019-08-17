import time
import threading

from tkinter import *

from SConfig import SConfig
from SnakeGame import SnakeGame
from SnakeNN import SnakeNN
from SnakeNN2 import SnakeNN2

class GameUI(threading.Thread):

	def __init__(self, window, board, model):
		self._interruptGame  = False
		self.window = window
		self.board = board
		self.model = model
		self.game = SnakeGame(board, autostart=True)
		threading.Thread.__init__(self)
		self.start()

	def run(self):
		self.game._draw()
		while not self._interruptGame:
			if self.game.stopped: continue

			# PREDICT STEP
			direction, relDirection = self.model.predictDirection(self.game)
			self.game.setDirection(direction)

			self.game.nextMove()
			self.game._draw()
			time.sleep(self.game.speed)

			if self.game.isFinished():
				time.sleep(1)
				ui.game.restart(autostart=True)

	def stop(self):
		self._interruptGame = True
		self.game.pause()
		self.window.destroy()
		
def keyPressed(keyCode):
	direction = SConfig.optsTk.get(keyCode.keysym, False)

	if keyCode.keysym == 'q': ui.stop()
	elif keyCode.keysym == 's': ui.game.speed = 0.05 if SConfig.speed == ui.game.speed else SConfig.speed
	elif 'RESTART' == direction: ui.game.restart()
	elif 'PAUSE'   == direction: ui.game.pause()

	# AI does directions
	#if False     != direction: ui.game.setDirection(direction)

if __name__ == "__main__":
	window = Tk()

	boardSize = SConfig.size * SConfig.px
	window.geometry(str(boardSize) + 'x' + str(boardSize))

	board = Canvas(window, width=boardSize, height=boardSize, bd=0, highlightthickness=0)
	board.pack()

	window.title('Snake Game')
	window.bind_all('<KeyPress>', keyPressed)

	model = SnakeNN2()
	model.loadModel()

	ui = GameUI(window, board, model)

	window.focus_force()
	window.mainloop()