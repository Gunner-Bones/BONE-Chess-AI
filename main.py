import chess
import mcts
import chessgame as cg
import heuristic as hrs

"""
Algorithm Types:
-'random': Plays random moves.
-'mcts': Monte Carlo tree search: Finds most promising nodes & traverses.
The Depth field controls how far it will traverse.
Evaluation Types:
-'simple': Hard-coded Chess evaluations.
"""

SETTINGS = {
	'ai_color': 'black',
	'evaluation': 'simple',
	'algorithm': 'random',
	'depth': 100
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
	cg.pca_ai_display(cboard, SETTINGS)

human_vs_ai()