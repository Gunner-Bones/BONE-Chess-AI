import copy
import chess
import pygame_chess_api.api as pcaa
from pygame_chess_api.api import Board
from pygame_chess_api.render import Gui

PCA_WHITE_SAN = ''
PCA_BLACK_SAN = ''

pca_types = {
	'p': pcaa.Pawn,
	'n': pcaa.Knight,
	'b': pcaa.Bishop,
	'r': pcaa.Rook,
	'q': pcaa.Queen,
	'k': pcaa.Check
}

def pca_get_piece(board, pos):
	for p in board.pieces_by_color[board.cur_color_turn]:
		if p.pos == pos:
			return p

def pca_san_pos(san):
	return (ord(san[0])-97,8-int(san[1]))

def pca_find_context_piece(board, styp, pos):
	for p in board.pieces_by_color[board.cur_color_turn]:
		if type(p) == pca_types[styp]:
			#print(type(p),board.cur_color_turn,[m.target for m in p.get_moves_allowed()])
			if pos in [m.target for m in p.get_moves_allowed()]:
				return p

def san_to_pca_move(board, s):
	# fuck this api lol
	s = s.replace('x','')
	if len(s) == 2:
		# pawn
		ps = pca_san_pos(s)
		cxp = pca_find_context_piece(board,'p',ps)
		if cxp:
			board.move_piece(cxp, ps)
	elif len(s) == 3:
		t,m = s[0].lower(), s[1:]
		ps = pca_san_pos(m)
		cxp = pca_find_context_piece(board,t,ps)
		if cxp:
			board.move_piece(cxp, ps)
	elif len(s) == 4:
		spos,epos = pca_san_pos(s[:2]),pca_san_pos(s[2:])
		if spos and epos:
			sp = pca_get_piece(board,spos)
			spty = [t for t in pca_types.keys() if pca_types[t] == type(sp)][0]
			san_to_pca_move(board, spty+s[2:])
	#print()

def pca_move_to_san(dmove):
	spos,epos = dmove['ini_pos'],dmove['move'].target
	return chr(spos[0]+97)+str(8-spos[1])+chr(epos[0]+97)+str(8-epos[1])

def pca_recent_san_move(pboard):
	recent_move = pboard.move_history[len(pboard.move_history)-1]
	return pca_move_to_san(recent_move)

def pca_ai_black_move(pboard):
	global PCA_BLACK_SAN
	global PCA_WHITE_SAN
	PCA_WHITE_SAN = pca_recent_san_move(pboard)
	san_to_pca_move(pboard, PCA_BLACK_SAN)

def pca_ai_white_move(pboard):
	global PCA_BLACK_SAN
	global PCA_WHITE_SAN
	PCA_BLACK_SAN = pca_recent_san_move(pboard)
	san_to_pca_move(pboard, PCA_WHITE_SAN)

def pca_display(cboard):
	pboard = Board()
	gui = Gui(pboard)
	moves = [m.uci() for m in cboard.move_stack]
	for m in moves:
		san_to_pca_move(pboard,m)
	gui.run_pygame_loop()

class ChessGame:
	# For use with the 'chess' library
	def __init__(self, hc):
		self.heuristic_class = hc
		self.moves = []
	def actions(self, board):
		return list(board.legal_moves)
	def move(self, board, move):
		new_board = copy.deepcopy(board)
		self.moves.append(new_board.push_san(move))
		return new_board
	def unmove(self, board):
		new_board = copy.deepcopy(board)
		rem_move = new_board.pop()
		self.moves.remove(rem_move)
		return new_board
	def utility(self, board):
		hc = heuristic_class(color=self.who_turn(board), board=board)
		return self.hc.score()
	def terminal_test(self, board):
		return board.is_game_over()
	def who_turn(self, board):
		return board.turn
	def display(self, board):
		# Uses the 'pygame_chess_api' library
		pca_display(board)
	def __repr__(self):
		return 'Heuristic: ' + str(self.heuristic) + '\nMoves: ' + (','.join([m.uci() for m in self.moves]))[:-1] + '\n'
