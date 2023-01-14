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
	cg.pca_ai_display(cboard, SETTINGS)

def human_vs_ai_debug(ai=False): # True=White False=Black
	board = chess.Board()
	ai_color = ai
	while True:
		print(board)
		if board.turn == ai_color:
			mcts_move = cg.ai_mcts_player(board)
			print('AI move:',mcts_move)
			board.push_san(mcts_move)
		else:
			valid_san = False
			while not valid_san:
				san = input('Human move ' + hrs.CC_CONV[board.turn] + ':')
				try:
					board.push_san(san)
					valid_san = True
				except Exception as e:
					print(e)

human_vs_ai()