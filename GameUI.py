import time
import threading

from tkinter import *

from SConfig import SConfig
from SnakeGame import SnakeGame

class GameUI(threading.Thread):

	def __init__(self, window, board):
		self._interruptGame  = False
		self.window = window
		self.board = board
		self.game = SnakeGame(board)
		threading.Thread.__init__(self)
		self.start()

	def run(self):
		self.game._draw()
		while not self._interruptGame:
			self.game.nextMove()
			self.game._draw()
			time.sleep(self.game.speed)

	def stop(self):
		self._interruptGame = True
		self.game.pause()
		self.window.destroy()
		
def keyPressed(keyCode):
	direction = SConfig.optsTk.get(keyCode.keysym, False)

	if keyCode.keysym == 'q': ui.stop()
	elif 'RESTART' == direction: ui.game.restart()
	elif 'PAUSE'   == direction: ui.game.pause()
	elif False     != direction: ui.game.setDirection(direction)

if __name__ == "__main__":
	window = Tk()

	boardSize = SConfig.size * SConfig.px
	window.geometry(str(boardSize) + 'x' + str(boardSize))

	board = Canvas(window, width=boardSize, height=boardSize, bd=0, highlightthickness=0)
	board.pack()

	window.title('Snake Game')
	window.bind_all('<KeyPress>', keyPressed)

	ui = GameUI(window, board)

	window.focus_force()
	window.mainloop()