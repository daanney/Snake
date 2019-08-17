from SnakeGame import SnakeGame
from SVector import SVector
from random import randint

import numpy as np
import sys, os, tflearn, math, pickle

from pathlib import Path

from statistics import mean
from tflearn.layers.core import input_data, fully_connected
from tflearn.layers.estimator import regression

class SnakeNN:
	tdGames = 20000 # to produce data
	tdSteps = 200
	tf_cache = 'SnakeNN/tflearn'
	td_cache = 'SnakeNN.td'
	tdx_cache = 'SnakeNN.tdx'

	input_nodes = 4

	td_X = []
	td_y = []

	tdx_X = []
	tdx_y = []

	directionsMap = {0:'UP', 1:'RIGHT', 2:'DOWN', 3:'LEFT'}

	def __init__(self):
		self.initModel()

	def predictDirection(self, game):
		print('--- prediction start ---')
		self.game = game
		direction = 0
		_state = self.checkGameState()
		predictions = []
		directions = []
		for newDirection in [-1, 0, 1]:
			newDirectionKey = self.getAbsoluteDirectionKey(newDirection)
			state = _state.copy()
			print(newDirectionKey)
			newSnakePosition = self.game.snake.getNextPosition(for_direction=newDirectionKey)
			#state.insert(0, newDirection)
			state.append(self.getNormalizedDistance(newSnakePosition, self.game.apple.getPosition()))
			print(state)
			pred = self.model.predict(np.array(state).reshape(-1, self.input_nodes, 1))
			predictions.append(pred)
			directions.append(newDirectionKey)
		bestPredictedIx = np.argmax(np.array(predictions))
		bestPredicted = directions[ bestPredictedIx ]
		print(predictions)
		print('best prediction: ', bestPredicted)
		print('--- prediction end ---')
		return bestPredicted, bestPredictedIx - 1 # relativeAction = index - 1

	def cachePredicted(self):
		with open(self.tdx_cache + '.X', 'wb') as f: pickle.dump(self.tdx_X, f)
		with open(self.tdx_cache + '.y', 'wb') as f: pickle.dump(self.tdx_y, f)

	def createTrainingData(self, replaceCache=False):
		if not replaceCache and Path(self.td_cache + '.X').exists(): 
			with open(self.td_cache + '.X', 'rb') as f: self.td_X = pickle.load(f)
			with open(self.td_cache + '.y', 'rb') as f: self.td_y = pickle.load(f)
		else: self._createTrainingData()
		print('games with total of ' + str(len(self.td_X)) + ' moves')

	def loadTDX(self):
		with open(self.tdx_cache + '.X', 'rb') as f: self.tdx_X = pickle.load(f)
		with open(self.tdx_cache + '.y', 'rb') as f: self.tdx_y = pickle.load(f)
		self.td_X += self.tdx_X
		self.td_y += self.tdx_y
		print('games with total of ' + str(len(self.td_X)) + ' moves')

	def _createTrainingData(self):
		stSteps = []
		stScore = []
		for _gameNo in range(self.tdGames):
			print('starting game number ' + str(_gameNo + 1))
			self.game = SnakeGame(autostart=True)
			modelScore = steps = gameScore = 0
			distanceToApple = self.getNormalizedDistance(self.game.snake.getPosition(), self.game.apple.getPosition())
			while not self.game.isFinished() and steps < self.tdSteps:
				direction = randint(-1, 1)
				state = self.checkGameState() # with old direction
				self.game.setDirection(self.getAbsoluteDirectionKey(direction))

				self.game.nextMove()
				
				modelScore, gameScore, distanceToApple = self.getScore(gameScore, distanceToApple)
				#state.insert(0, direction)
				state.append(distanceToApple)
				self.td_X.append(state)
				self.td_y.append(modelScore)
				steps += 1
			stSteps.append(steps)
			stScore.append(self.game.getScore())
			print('Game finished with score/steps', self.game.getScore(), '/', steps)
		print('average steps', mean(stSteps))
		print('average score', mean(stScore))
		print('max steps', max(stSteps))
		print('max score', max(stScore))
		print('total of', len(self.td_X), 'moves')
		print('total of', len(self.td_y), 'targets')

		with open(self.td_cache + '.X', 'wb') as f: pickle.dump(self.td_X, f)
		with open(self.td_cache + '.y', 'wb') as f: pickle.dump(self.td_y, f)

	def testModel(self, games=1000, maxSteps=4000):
		stSteps = []
		stScore = []
		print('starting test games ...')
		noPrint = open(os.devnull, 'w')
		for _gameNo in range(games):
			print('starting game number ' + str(_gameNo + 1))
			sys.stdout = noPrint
			self.game = SnakeGame(autostart=True)
			modelScore = steps = gameScore = 0
			distanceToApple = self.getNormalizedDistance(self.game.snake.getPosition(), self.game.apple.getPosition())
			while not self.game.isFinished() and steps < maxSteps:
				state = self.checkGameState()
				direction, relDirection = self.predictDirection(self.game)
				self.game.setDirection(direction)
				self.game.nextMove()
				
				modelScore, gameScore, distanceToApple = self.getScore(gameScore, distanceToApple)
				#state.insert(0, direction)
				state.append(distanceToApple)
				self.tdx_X.append(state)
				self.tdx_y.append(modelScore)
				steps += 1
			stSteps.append(steps)
			stScore.append(self.game.getScore())
			sys.stdout = sys.__stdout__
			print('Game finished with score/steps', self.game.getScore(), '/', steps)
		print('average steps', mean(stSteps))
		print('average score', mean(stScore))
		print('max steps', max(stSteps))
		print('max score', max(stScore))
		print('total of', len(self.tdx_X), 'moves')
		print('total of', len(self.tdx_y), 'targets')

		with open(self.tdx_cache + '.X', 'wb') as f: pickle.dump(self.tdx_X, f)
		with open(self.tdx_cache + '.y', 'wb') as f: pickle.dump(self.tdx_y, f)

	def getScore(self, prevScore, prevDistanceToApple):
		gameScore = self.game.getScore()
		distanceToApple = self.getNormalizedDistance(self.game.snake.getPosition(), self.game.apple.getPosition())
		modelScore = 0
		if self.game.isFinished(): modelScore = -1
		elif gameScore > prevScore: modelScore = 1
		elif distanceToApple < prevDistanceToApple: modelScore = 0.5

		return [modelScore, gameScore, distanceToApple]


	# relatively from the snake :: -1:left, 0:straight, 1:right
	def randomDirection(self, currentIx):
		newIx = currentIx + randint(-1, 1)
		if newIx < 0: newIx = 3
		if newIx > 3: newIx = 0
		return newIx

	# relativeTurn: -1="to-left", 0="straight", 1="to-right"
	def getAbsoluteDirectionKey(self, relativeTurn):
		newIx = self.getDirectionIndex() + relativeTurn
		if newIx < 0: newIx = 3
		if newIx > 3: newIx = 0
		return self.directionsMap.get(newIx)

	# [object-left, object-front, object-right]
	def checkGameState(self):
		return [
			 self.game.snake.isDirectionFree(self.getAbsoluteDirectionKey(-1))  # to-left
			,self.game.snake.isDirectionFree(self.game.snake.getDirectionKey()) # straight
			,self.game.snake.isDirectionFree(self.getAbsoluteDirectionKey(1))   # to-right
		]

	def getDirectionIndex(self):
		for ix, direction in self.directionsMap.items():
			if self.game.snake.getDirectionKey() == direction:
				return ix

	def getDistance(self, p1, p2):
		return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)

	def getNormalizedDistance(self, p1, p2):
		if not hasattr(self, '_nrmlMax'):
			self._nrmlMax = self.getDistance(SVector(0,0), SVector(self.game.getBoardSize(), self.game.getBoardSize()))
		if (p1.x < 0 or p1.y < 0 or p2.x < 0 or p2.x < 0 or
				p1.x > self._nrmlMax or p1.y > self._nrmlMax or p2.x > self._nrmlMax or p2.x > self._nrmlMax):
			return 1
		distance = self.getDistance(p1, p2)
		return abs((distance) / (self._nrmlMax))

	def getDistanceSigmoid(self, delta):
		return (1 / (1 + math.exp(-delta)))

	def train(self):
		print('td_X size: ' + str(len(self.td_X)))
		print('td_y size: ' + str(len(self.td_y)))
		self.trainModel(self.td_X, self.td_y)

	def initModel(self):
		if hasattr(self, 'model'): return
		self.input_layer = input_data(shape=[None, self.input_nodes, 1], name='input')
		self.hidden_layer = fully_connected(self.input_layer, int((self.input_nodes + 1) / 2), activation='tanh')
		self.output_layer = fully_connected(self.hidden_layer, 1, activation='linear')
		network = regression(self.output_layer, optimizer='adam', learning_rate=1e-2, loss='mean_square', name='target')
		self.model = tflearn.DNN(network, tensorboard_dir='log')

	def trainModel(self, X, y):
		self.model.fit(np.array(X).reshape(-1, self.input_nodes, 1), np.array(y).reshape(-1, 1),
			n_epoch=5, shuffle=True, run_id=self.tf_cache)
		self.model.save(self.tf_cache)

	def loadModel(self):
		self.initModel()
		self.model.load(self.tf_cache)

	def showModelDetails(self):
		self.initModel()
		print('hidden layer weights')
		print(self.model.get_weights(self.hidden_layer.W))
		print(self.model.get_weights(self.hidden_layer.b))
		print('output layer weights')
		print(self.model.get_weights(self.output_layer.W))
		print(self.model.get_weights(self.output_layer.b))



if __name__ == "__main__":
	nn = SnakeNN()

	nn.createTrainingData()

	nn.loadTDX()

	nn.train()
	
	nn.testModel()

	nn.showModelDetails()
	#print(nn.td_X)
	#print(np.array(nn.td_X).reshape(-1, 5, 1))
