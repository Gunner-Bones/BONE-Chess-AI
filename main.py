import chessgame as cg
import chess

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
	
demo_scholarsmate()