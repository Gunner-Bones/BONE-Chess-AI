# Credit to aima-python and Ishaan Gupta
import chess
import chessgame
import math
import random
import heuristic as hrs
import numpy as np

# hyperparameters
C = 1.5 # exploration constant
N = 1000 # MCTS depth

class Node:
	def __init__(self, state=chess.Board(), children=[], parent=None):
		self.state = state
		self.children = children
		self.parent = parent
		self.n = 0
		self.u = 0

def UCB(node):
	"""
	Qta + C * sqrt(ln(pn)/n)
	where
	-Qta is success rate or u / n
	-C is exploration constant (1 < C < 2 for good results)
	-pn is parent node n
	-u is utility or win score
	-n is number of times traversed
	"""
	return -np.inf if not node.n else (node.u / node.n) + (C * math.sqrt(np.log(node.parent.n) / node.n))

def MCTS(state, game, N=1000, heuristic_class=hrs.ChessSimpleHeuristic):
	def select(node):
		if node.children:
			return select(max(node.children, key=UCB))
		else:
			return node
	def expand(node):
		if not node.children and not game.terminal_test(node.state):
			node.children = [Node(state=game.move(board=state,move=move),parent=node) for move in list(state.legal_moves)]
		return select(node)
	def rollout(game, state):
		sim_state = state
		while not game.terminal_test(state):
			action = random.choice(game.actions(state))
			sim_state = game.move(state, action)
		u = game.utility(sim_state)
		return -u
	def backpropagation(node, utility):
		if utility > 0:
			node.u += utility
		node.n += 1
		if node.parent:
			backpropagation(node.parent, -utility)

	root = Node(state=state)
	for _ in range(N):
		leaf = select(root)
		child = expand(leaf)
		result = rollout(game, child.state)
		backpropagation(child, result)
	max_state = max(root.children, key=lambda c: c.n)
	return max_state