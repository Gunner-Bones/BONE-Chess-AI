import chess
import mcts
import chessgame as cg
import heuristic as hrs

"""
Algorithm Types:
-'random': Plays random moves.
-'mcts': Monte Carlo tree search: Finds most promising nodes & traverses.
The Depth field controls how far it will traverse vertically.
The Breadth field controls how far it will search horizontally.
Evaluation Types:
-'simple': Hard-coded Chess evaluations.
"""

SETTINGS = {
	'ai_color': 'black',
	'evaluation': 'simple',
	'algorithm': 'mcts',
	'depth': 15,
	'breadth': 50
}

def demo_scholarsmate():
	board = chess.Board()
	board.push_san("e4")
	board.push_san("e5")
	board.push_san("Qh5")
	board.push_san("Nc6")
	board.push_san("Bc4")
	board.push_san("Nf6")
	board.push_san("Qxf7")
	cg.pca_display(board) 

def demo_normal():
	board = chess.Board()
	cg.pca_display(board)

def human_vs_ai():
	cboard = chess.Board()
	cboard.push_san("e4")
	cboard.push_san("e5")
	cboard.push_san("f4")
	cboard.push_san("a6")
	cg.pca_ai_display(cboard, SETTINGS)

human_vs_ai()