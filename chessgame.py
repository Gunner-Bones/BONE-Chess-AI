import copy
import time
import chess
import pygame
import random
import pygame_chess_api.api as pcaa
from pygame_chess_api.api import Board, Piece
from pygame_chess_api.render import Gui
import heuristic as hrs
import mcts

PCA_AI_HEUR = None
PCA_AI_DEPTH = None
PCA_AI_BREADTH = None
pca_types = {
	'p': pcaa.Pawn,
	'n': pcaa.Knight,
	'b': pcaa.Bishop,
	'r': pcaa.Rook,
	'q': pcaa.Queen,
	'k': pcaa.Check
}

def ai_mcts_player(cboard):
	global PCA_AI_HEUR
	global PCA_AI_DEPTH
	global PCA_AI_BREADTH
	game = ChessGame(hc=PCA_AI_HEUR)
	mcts_board = None
	while not mcts_board:
		mcts_board = mcts.MCTS(cboard, game, D=PCA_AI_DEPTH, E=PCA_AI_BREADTH)
	#print('bot move',mcts_board.peek().uci())
	san_move = hrs.move_to_san_better(mcts_board, mcts_board.peek())
	return san_move

def ai_random_player(cboard):
	random_move = random.choice(list(cboard.legal_moves))
	time.sleep(0.5)
	cboard.push(random_move)
	return hrs.move_to_san_better(cboard, random_move)

PCA_AI_CBOARD = None
PCA_AI_FUNC = ai_mcts_player
PCA_AI_HEUR = hrs.ChessSimpleHeuristic
PCA_AI_DEPTH = 15
PCA_AI_BREADTH = 100

pca_ai_functions = {
	'mcts': ai_mcts_player,
	'random': ai_random_player
}
pca_ai_heuristics = {
	'simple': hrs.ChessSimpleHeuristic
}

def pca_get_piece(board, pos):
	for p in board.pieces_by_color[Piece.WHITE] + board.pieces_by_color[Piece.BLACK]:
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
	if 'x' in s:
		xi = s.index('x')
		if xi:
			s = s[xi:]
	s = s.replace('x','').replace('+','').replace('#','').lower()
	if s[-2:].startswith('='):
		s = s[:-2]
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

def pca_move_to_uci(dmove):
	spos,epos = dmove['ini_pos'],dmove['move'].target
	ucim = chr(spos[0]+97)+str(8-spos[1])+chr(epos[0]+97)+str(8-epos[1])
	if type(dmove['piece']) == pcaa.Pawn:
		if dmove['piece'].promote_class_wanted:
			ucim += [pk for pk,pt in pca_types.items() if pt == dmove['piece'].promote_class_wanted][0]
	return ucim

def uci_to_pca_pos(ucim):
	epos = ucim[2:]
	return (ord(epos[0])-97,8-int(epos[1]))

def pca_recent_san_move(pboard):
	recent_move = pboard.move_history[len(pboard.move_history)-1]
	return pca_move_to_uci(recent_move)

def pca_pop(pboard):
	pass

def pca_ai_move(pboard):
	global PCA_AI_CBOARD
	global PCA_AI_FUNC
	san = PCA_AI_FUNC(PCA_AI_CBOARD)
	PCA_AI_CBOARD.push_san(san)
	print('AI move:',san)
	san_to_pca_move(pboard, san)

def pca_display(cboard):
	pboard = Board()
	gui = Gui(pboard, verbose=0)
	moves = [m.uci() for m in cboard.move_stack]
	for m in moves:
		san_to_pca_move(pboard,m)
	gui.run_pygame_loop()

def pca_ai_display(cboard, settings):
	global PCA_AI_CBOARD
	global PCA_AI_FUNC
	global PCA_AI_HEUR
	global PCA_AI_DEPTH
	global PCA_AI_BREADTH
	PCA_AI_CBOARD = cboard
	PCA_AI_DEPTH = settings['depth']
	PCA_AI_BREADTH = settings['breadth']
	if settings['algorithm']:
		PCA_AI_FUNC = pca_ai_functions[settings['algorithm']]
	if settings['evaluation']:
		PCA_AI_HEUR = pca_ai_heuristics[settings['evaluation']]
	pboard = Board()
	if cboard.move_stack:
		for m in cboard.move_stack:
			move = m.uci()
			pos = pca_san_pos(move[2:])
			pty = [pt for pk,pt in hrs.CPT_CONV.items() if hrs.get_piece_type(cboard, m) == pk][0]
			piece = pca_find_context_piece(pboard,pty,pos)
			pboard.move_piece(piece,pos)
	cmbg = [Piece.WHITE]
	match settings['ai_color']:
		case 'white':
			cmbg = [Piece.BLACK]
		case 'black':
			cmbg = [Piece.WHITE]
	gui = BetterGui(pboard, colors_managed_by_gui=cmbg, verbose=0)
	gui.run_better_pygame_loop(better_ai_function=pca_ai_move)

class BetterGui(Gui):
	""" Extends pygame_chess_api.render.Gui for better chess game functionality with this program. """
	def mouse_released(self):
		global PCA_AI_CBOARD
		super().mouse_released()
		if self.board.cur_color_turn == PCA_AI_CBOARD.turn:
			rpsan = pca_recent_san_move(self.board)
			rppos = uci_to_pca_pos(rpsan)
			rp = pca_get_piece(self.board, rppos)
			if self.board.is_allowed_move(rp, rppos):
				PCA_AI_CBOARD.push_uci(rpsan)
				rbsan = hrs.move_to_san_better(PCA_AI_CBOARD,chess.Move.from_uci(rpsan))
				print('Human move:',rbsan)
	def run_better_pygame_loop(self, better_ai_function=None):
		self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
		pygame.display.set_caption(self.window_title)
		self.clock = pygame.time.Clock()
		stop_loop = False
		while not stop_loop:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					stop_loop = True
					break
				if event.type == pygame.MOUSEBUTTONDOWN:
					mouse_presses = pygame.mouse.get_pressed()
					if mouse_presses[0] == True: #left click
						self.mouse_left_clicked()
				if event.type == pygame.MOUSEBUTTONUP:
					self.mouse_released()
			self.draw_board()
			if self.board.cur_color_turn not in self.colors_managed and not self.board.game_ended:
				cur_turn = self.board.cur_color_turn
				if better_ai_function is None:
					raise ValueError("You must specify a function_for_AIs when calling Gui.run_pygame_loop because you configured that the Gui object shouln't manage every color")
				while cur_turn == self.board.cur_color_turn:
					better_ai_function(self.board)
				self.need_screen_update = True
			self.clock.tick(self.FPS)

class ChessGame:
	# For use with the 'chess' library
	def __init__(self, hc=hrs.ChessSimpleHeuristic):
		self.heuristic_class = hc
		self.moves = []
	def actions(self, board):
		return hrs.get_all_legal_moves(board, board.turn)
	def move(self, board, move):
		#print('cg move',move)
		try:
			self.moves.append(board.push_san(move))
		except chess.IllegalMoveError as ime:
			#print(board)
			#print(ime)
			pass
		return board
	def unmove(self, board):
		rem_move = board.pop()
		self.moves.remove(rem_move)
		return board
	def utility(self, board):
		max_h = hrs.HEURISTIC_MAX
		hc = self.heuristic_class(color=self.who_turn(board), board=board)
		utility = hc.score() / max_h 
		return utility if utility <= 1 else 1
	def terminal_test(self, board):
		return board.is_game_over()
	def who_turn(self, board):
		return board.turn
	def display(self, board):
		# Uses the 'pygame_chess_api' library
		pca_display(board)
	def __repr__(self):
		return 'Heuristic: ' + str(self.heuristic) + '\nMoves: ' + (','.join([m.uci() for m in self.moves]))[:-1] + '\n'
