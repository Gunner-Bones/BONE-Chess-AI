# Credit to aima-python and Ishaan Gupta
import chess
import chessgame
import math
import random
import threading
import heuristic as hrs

# hyperparameters
C = 1.4 # exploration constant
N = 1000 # MCTS depth

class Node:
	def __init__(self, state=chess.Board(), children=[], parent=None):
		self.state = state
		self.children = children
		self.parent = parent
		self.n = 0
		self.u = 0
	def __repr__(self):
		strr = 'state: ' + hrs.move_to_san_better(self.state, self.state.peek()) + '\n'
		strr += 'children: ' + str(len(self.children)) + '\n'
		strr += 'has parent: ' + str(bool(self.parent)) + '\n'
		strr += 'traversed: ' + str(self.n) + '\n'
		strr += 'utility: ' + str(self.u) + '\n'
		return strr

def UCB(node):
	"""
	Qta + C * sqrt(ln(pn)/n)
	where
	-Qta is success rate or u / n
	-C is exploration constant (1 < C < 2 for good results)
	-pn is parent node n
	-u is utility or win score (0 < u < 1)
	-n is number of times traversed
	"""
	return float('inf') if not node.n else (node.u / node.n) + (C * math.sqrt(math.log(node.parent.n) / node.n))

MCTS_LAST_VALUE = 0

def MCTS(state, game, D, E):
	def select(node, di):
		if node.children and di < D:
			return select(node=max(node.children, key=UCB), di=di+1)
		else:
			return node
	def expand(node, di):
		if not node.children and not game.terminal_test(node.state):
			node.children = [Node(state=game.move(board=node.state.copy(),move=move),parent=node) for move in game.actions(node.state)]
		return select(node, di)
	def rollout(game, state, di):
		sim_state = state.copy()
		while not game.terminal_test(state) and di < D:
			available_actions = game.actions(state)
			if not available_actions:
				break
			action = random.choice(available_actions)
			sim_state = game.move(state, action)
			di += 1
		u = game.utility(sim_state)
		return u
	def backpropagation(node, utility):
		if utility > 0:
			node.u += utility
		node.n += 1
		if node.parent:
			backpropagation(node.parent, -utility)

	root = Node(state=state)
	for i in range(E):
		di = 0
		print('-iteration',i)
		leaf = select(root, di)
		print('-selected')
		child = expand(leaf, di)
		print('-expanded')
		result = rollout(game, child.state, di)
		print('-rollout result',result)
		backpropagation(child, result)
		print('-backpropped with new traversal',child.n)
	print([[c.state.peek().uci(), c.u] for c in root.children])
	best_node = max(root.children, key=lambda c: c.u / c.n if c.n else c.u)
	return best_node.state