import chess
import chessgame
import math
import random
import numpy as np

C = 1.5

class Node:
	def __init__(self):
		self.state = chess.Board()
		self.children = []
		self.parent = None
		self.n = 0
		self.u = 0

def UCB(node):
	"""
	Qta + C * sqrt(ln(pn)/n)
	where
	-Qta is success rate, aka u / n
	-C is exploration constant (1 < C < 2 for good results)
	-pn is parent node n
	-u is utility or win score
	-n is number of times traversed
	"""
	return np.inf if not node.n else (node.u / node.n) + (C * math.sqrt(np.log(node.parent.n) / node.n))

def MCTS(state, game, N=1000):
	def select(node):
		if node.children:
			return select(max(node.children, key=UCB))
		else:
			return node
	def expand(node):
		if not node.children