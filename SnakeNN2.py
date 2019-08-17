from SnakeGame import SnakeGame
from SVector import SVector
from random import randint

import numpy as np
import sys, os, tflearn, math, pickle

from pathlib import Path

from statistics import mean
from tflearn.layers.core import input_data, fully_connected
from tflearn.layers.estimator import regression

## Model:
#
#                 input    hidden   output: vote for
# object-left         O
# object-straight     O      O
# object-right        O      O
# distance-left       O      O      O  > turn left  
# distance-straight   O      O      O  > go straight
# distance-right      O      O      O  > turn right
# current-pos         O      O
# current-distance    O


class SnakeNN2:
	tdGames = 20000 # to produce data
	tdSteps = 200
	tf_cache = 'SnakeNN2/tflearn'
	td_cache = 'SnakeNN2.td'
	tdx_cache = 'SnakeNN2.tdx'

	input_nodes = 8

	td_X = []
	td_y = []

	tdx_X = []
	tdx_y = []
	tdx_ypred = []

	directionsMap = {0:'UP', 1:'RIGHT', 2:'DOWN', 3:'LEFT'}

	def __init__(self):
		self.initModel()

	def predictDirection(self, game):
		print('--- prediction start ---')
		self.game = game
		state = np.array(self.checkGameState())
		state.flatten()
		prediction = self.model.predict(state.reshape(-1, self.input_nodes, 1))
		directionIx = np.argmax(np.array(prediction))
		predictedKey = self.getAbsoluteDirectionKey(directionIx - 1)
		print(state)
		print(prediction)
		print(predictedKey)
		print('--- prediction end ---')
		return predictedKey, prediction

	def cachePredicted(self):
		with open(self.tdx_cache + '.X', 'wb') as f: pickle.dump(self.tdx_X, f)
		with open(self.tdx_cache + '.y', 'wb') as f: pickle.dump(self.tdx_y, f)

	def createTrainingData(self, replaceCache=False):
		if not replaceCache and Path(self.td_cache + '.X').exists(): 
			with open(self.td_cache + '.X', 'rb') as f: self.td_X = pickle.load(f)
			with open(self.td_cache + '.y', 'rb') as f: self.td_y = pickle.load(f)
		else: self._createTrainingData()
		print('games with total of ', str(len(self.td_X)), ' steps')

	def loadTDX(self):
		with open(self.tdx_cache + '.X', 'rb') as f: self.tdx_X = pickle.load(f)
		with open(self.tdx_cache + '.y', 'rb') as f: self.tdx_y = pickle.load(f)
		self.td_X += self.tdx_X
		self.td_y += self.tdx_y
		print('games with total of ', str(len(self.td_X)), ' steps')

	def _createTrainingData(self):
		stSteps = []
		stScore = []
		for _gameNo in range(self.tdGames):
			print('starting game number ' + str(_gameNo + 1))
			self.game = SnakeGame(autostart=True)
			steps = 0
			while not self.game.isFinished() and steps < self.tdSteps:
				state = self.checkGameState()
				# <<< 0=left ; 1=straight ; 2=right
				direction = randint(0, 2)
				tgt = self.getScore(state)
				self.game.setDirection(self.getAbsoluteDirectionKey(direction - 1))
				self.game.nextMove()

				self.td_X.append(state)
				self.td_y.append(tgt)
				steps += 1
			gameScore = self.game.getScore()
			stSteps.append(steps)
			stScore.append(gameScore)
			print('Game finished with score/steps', gameScore, '/', steps)
		print('average steps', mean(stSteps))
		print('average score', mean(stScore))
		print('max steps', max(stSteps))
		print('max score', max(stScore))
		print('total of', len(self.td_X), 'steps')

		with open(self.td_cache + '.X', 'wb') as f: pickle.dump(self.td_X, f)
		with open(self.td_cache + '.y', 'wb') as f: pickle.dump(self.td_y, f)

	def testModel(self, games=100, maxSteps=5000):
		stSteps = []
		stScore = []
		print('starting test games ...')
		noPrint = open(os.devnull, 'w')
		for _gameNo in range(games):
			print('starting game number', _gameNo)
			sys.stdout = noPrint
			self.game = SnakeGame(autostart=True)
			steps = 0
			while not self.game.isFinished() and steps < maxSteps:
				state = self.checkGameState()
				direction, preditions = self.predictDirection(self.game)
				self.game.setDirection(direction)
				self.game.nextMove()
				
				modelScore = self.getScore(state)
				self.tdx_X.append(state)
				self.tdx_y.append(modelScore)
				self.tdx_ypred.append(preditions.squeeze().tolist())
				steps += 1
			gameScore = self.game.getScore()
			stSteps.append(steps)
			stScore.append(gameScore)
			sys.stdout = sys.__stdout__
			print('Game finished with score/steps', gameScore, '/', steps)
		print('average steps', mean(stSteps))
		print('average score', mean(stScore))
		print('max steps', max(stSteps))
		print('max score', max(stScore))
		print('total of', len(self.tdx_X), 'steps')

		with open(self.tdx_cache + '.X', 'wb') as f: pickle.dump(self.tdx_X, f)
		with open(self.tdx_cache + '.y', 'wb') as f: pickle.dump(self.tdx_y, f)
		with open(self.tdx_cache + '.ypred', 'wb') as f: pickle.dump(self.tdx_ypred, f)

	def getScore(self, state):
		prevDistance = state[-1]
		modelScore = [0, 0, 0]
		for i, _ in enumerate(modelScore):
			modelScore[i] += 0 if state[i] == 1 else -1
			if state[i+3] == 0: modelScore[i] += 1
			elif state[i+3] < prevDistance: modelScore[i] += 0.5

		# if straight goes closer to apple, prefer it
		iStraight = 1
		if modelScore[iStraight] > 0 and state[iStraight + 3] < prevDistance: 
			modelScore[iStraight] += 0.5


		return modelScore


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

	# [object left,front,right, distance if left,front,right, currentIndex, currentDistance]
	def checkGameState(self):
		applePos = self.game.apple.getPosition()
		distanceToApple = self.getNormalizedDistance(self.game.snake.getPosition(), applePos)
		state = [0,0,0, 0,0,0, self.getDirectionIndex(), distanceToApple]
		for i, dk in enumerate([self.getAbsoluteDirectionKey(-1), 
				self.game.snake.getDirectionKey(), self.getAbsoluteDirectionKey(1)]):
			pos = self.game.snake.getNextPosition(for_direction=dk)
			state[i] = self.game.snake.isDirectionFree(dk)
			state[i + 3] = self.getNormalizedDistance(pos, applePos)
		return state

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

	def train(self):
		print('td_X size: ', len(self.td_X))
		print('td_y size: ', len(self.td_y))
		self.trainModel(self.td_X, self.td_y)

	def initModel(self):
		if hasattr(self, 'model'): return
		self.input_layer = input_data(shape=[None, self.input_nodes, 1], name='input')
		self.hidden_layer = fully_connected(self.input_layer, int((self.input_nodes + 3) / 2), activation='tanh')
		self.output_layer = fully_connected(self.hidden_layer, 3, activation='linear')
		network = regression(self.output_layer, optimizer='adam', learning_rate=1e-2, loss='mean_square', name='target')
		self.model = tflearn.DNN(network, tensorboard_dir='log')

	def trainModel(self, X, y):
		self.model.fit(np.array(X).reshape(-1, self.input_nodes, 1), np.array(y).reshape(-1, 3),
			n_epoch=10, shuffle=True, run_id=self.tf_cache)
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
	nn = SnakeNN2()
	nn.createTrainingData()
	nn.loadTDX()
	nn.train()
	nn.testModel()

	#nn.loadModel()
	#nn.testModel(games=1000, maxSteps=10000)

	nn.showModelDetails()
