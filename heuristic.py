import chess

C_PIECES = {
	'p': 8,
	'r': 2,
	'b': 2,
	'n': 2,
	'q': 1,
	'k': 1
}
C_SPACES = [chr(l+97)+str(n) for n in range(1,9) for l in range(8)]
C_MOVES = [t+m for m in C_SPACES for t in ['','r','b','n','q','k']]
CPT_CONV = {
	chess.PAWN: 'p',
	chess.KNIGHT: 'n',
	chess.BISHOP: 'b',
	chess.ROOK: 'r',
	chess.QUEEN: 'q',
	chess.KING: 'k'
}
CC_CONV = {True: 'WHITE', False: 'BLACK'}

def square_math(pos, h=0, v=0): # positive v is white moving up & positive h is white moving right, inverted for black
	nsq = chr(ord(pos[0])+h)+str(int(pos[1])+v)
	if '-' in nsq or len(nsq) == 3:
		return pos
	return nsq if 97 <= ord(nsq[0]) <= 104 and 1 <= int(nsq[1]) <= 8 else pos

def relative_square_math(color, pos, h=0, v=0):
	return square_math(pos,h,v) if color else square_math(pos,-h,-v)
sm = square_math
rsm = relative_square_math

def global_is_legal(board, color, move):
	il = None
	if board.turn != color:
		board.push(chess.Move.from_uci("0000"))
		il = board.is_legal(move)
		board.pop()
	else:
		il = board.is_legal(move)
	return il

def get_color_pieces(board, color, ptypes=CPT_CONV.keys()):
	ret = {}
	for pt in ptypes:
		pieces = board.pieces(piece_type=pt, color=color)
		for sq in pieces:
			piece = board.piece_at(sq)
			ret[chess.square_name(sq)] = piece
	return ret

def get_piece_pseudo_moves(piece, pos, color):
	# fuck me
	moves = []
	match piece.piece_type:
		case chess.PAWN:
			moves = [rsm(color,pos,h=-1,v=1),
					 rsm(color,pos,h=0,v=1),
					 rsm(color,pos,h=1,v=1)]
			if (pos[1] == '2' and color) or (pos[1] == '7' and not color):
				moves.append(rsm(color,pos,h=0,v=2)) # pawn starting 2-space jump
		case chess.KNIGHT:
			moves = [rsm(color,pos,h=-1,v=2),
					 rsm(color,pos,h=1,v=2),
					 rsm(color,pos,h=-1,v=-2),
					 rsm(color,pos,h=1,v=-2),
					 rsm(color,pos,h=-2,v=1),
					 rsm(color,pos,h=2,v=1),
					 rsm(color,pos,h=-2,v=-1),
					 rsm(color,pos,h=-2,v=1)]
		case chess.BISHOP:
			moves = [rsm(color,pos,h=i,v=i) for i in range(-8,9)]
		case chess.ROOK:
			moves = [rsm(color,pos,h=i,v=0) for i in range(-8,9)]
			moves += [rsm(color,pos,h=0,v=i) for i in range(-8,9)]
		case chess.QUEEN:
			moves = [rsm(color,pos,h=i,v=0) for i in range(-8,9)]
			moves += [rsm(color,pos,h=0,v=i) for i in range(-8,9)]
			moves += [rsm(color,pos,h=i,v=i) for i in range(-8,9)]
		case chess.KING:
			moves = [rsm(color,pos,h=i,v=0) for i in range(-1,2)]
			moves += [rsm(color,pos,h=0,v=i) for i in range(-1,2)]
			moves += [rsm(color,pos,h=i,v=i) for i in range(-1,2)]
			if (pos == 'e1' and color) or (pos == 'e8' and not color):
				moves.append(rsm(color,pos,h=2,v=0)) #castling
	return [m for m in moves if m != pos]

def get_piece_legal_moves(board, piece, pos, color):
	moves = get_piece_pseudo_moves(piece, pos, color)
	legal_moves = [pos+move for move in moves if global_is_legal(board, color, chess.Move.from_uci(pos+move))]

	# en passant since for some reason board.is_legal() thinks it's not legal
	if piece.piece_type == chess.PAWN: 
		leftpos,rightpos = rsm(color,pos,h=-1,v=0),rsm(color,pos,h=1,v=0)
		leftpiece,rightpiece = board.piece_at(chess.parse_square(leftpos)),board.piece_at(chess.parse_square(rightpos))
		if leftpiece and leftpos != pos:
			if leftpiece.color != color:
				leftuppiece = board.piece_at(chess.parse_square(rsm(color,pos,h=-1,v=1)))
				if leftuppiece:
					if leftuppiece.color != color:
						legal_moves.append(pos+rsm(color,pos,h=-1,v=1))
				else:
					legal_moves.append(pos+rsm(color,pos,h=-1,v=1))
		if rightpiece and rightpos != pos:
			if rightpiece.color != color:
				rightuppiece = board.piece_at(chess.parse_square(rsm(color,pos,h=1,v=1)))
				if rightuppiece:
					if rightuppiece.color != color:
						legal_moves.append(pos+rsm(color,pos,h=1,v=1))
				else:
					legal_moves.append(pos+rsm(color,pos,h=1,v=1))

	return legal_moves

def get_legal_moves(board, at): # depricated
	return [at+pm for pm in C_SPACES if at != pm and board.is_legal(chess.Move.from_uci(at+pm))]

def get_legal_moves_better(board, at):
	piece = board.piece_at(chess.parse_square(at))
	if not piece:
		return []
	return get_piece_legal_moves(board, piece, at, piece.color)

def get_pseudo_moves_better(board, at):
	piece = board.piece_at(chess.parse_square(at))
	if not piece:
		return []
	return [at+move for move in get_piece_pseudo_moves(piece, at, piece.color)]

def get_type_legal_moves(board, color, pt):
	pieces = [chess.square_name(sq) for sq in board.pieces(pt, color)]
	tm = []
	for sq in pieces:
		tm += get_legal_moves_better(board, sq)
	return tm

def get_type_pseudo_moves(board, color, pt):
	pieces = [chess.square_name(sq) for sq in board.pieces(pt, color)]
	tm = []
	for sq in pieces:
		tm += get_pseudo_moves_better(board, sq)
	return tm

def get_all_legal_moves(board, color):
	am = []
	for pt in CPT_CONV.keys():
		am += get_type_legal_moves(board, color, pt)
	return am

def get_all_pseudo_moves(board, color):
	am = []
	for pt in CPT_CONV.keys():
		am += get_type_pseudo_moves(board, color, pt)
	return am

def chess_heuristic():
	return {'p': 0, 'r': 0, 'b': 0, 'n': 0, 'q': 0, 'k': 0}

# heuristic constants
WEIGHT_MATERIAL = {
	'p': 10,
	'n': 33,
	'b': 38,
	'r': 50,
	'q': 90,
	'k': 900
}
WEIGHT_MOBILITY = {
	'p': 20,
	'n': 15,
	'b': 15,
	'r': 12,
	'q': 20,
	'k': 5
}
WEIGHT_PROTECTS = {
	'p': 15,
	'n': 25,
	'b': 35,
	'r': 40,
	'q': 90,
	'k': 900
}

class ChessHeuristic:
	def __init__(self, color, board, htype=1):
		raise NotImplementedError
	def score(self):
		raise NotImplementedError

class ChessSimpleHeuristic(ChessHeuristic):
	def __init__(self, color, board, htype=1):
		self.c = color
		self.b = board
		self.h = 0
		self.htype = htype
	def update(self, board):
		self.h = 0
		self.b = board
	def h_material(self, color):
		""" Evaluates how good the board is for a color. """
		score = chess_heuristic()
		pieces = get_color_pieces(self.b, color)
		for p in pieces.values():
			score[CPT_CONV[p.piece_type]] += 1
		return score
	def h_possession(self, color):
		""" Evaluates how many pieces are captured by a color. """
		score = chess_heuristic()
		o_pieces_count = self.h_material(not color)
		for pt in o_pieces_count.keys():
			captured = C_PIECES[pt] - o_pieces_count[pt]
			score[pt] += captured
		return score
	def h_mobility(self, color):
		""" Evaluates how many pieces can move. """
		score = chess_heuristic()
		for pt in CPT_CONV.keys():
			pts = len(get_type_legal_moves(self.b, color, pt))
			score[CPT_CONV[pt]] += pts
		return score
	def h_protects(self, color):
		""" Evaluates how many pieces are protected. """
		score = chess_heuristic()
		pieces = get_color_pieces(self.b, color)
		lm = [m[2:] for m in get_all_pseudo_moves(self.b, color)]
		o_lm = [m[2:] for m in get_all_legal_moves(self.b, not color)]
		for p in pieces.items():
			pos,piece = p[0],p[1]
			if pos in lm and pos in o_lm:
				score[CPT_CONV[piece.piece_type]] += 1
		return score
	def score(self):
		""" Returns the heuristic score. """
		FUNCTIONS_SIMPLEHEURISTIC = {
			# NORMAL
			1: [[self.h_material, WEIGHT_MATERIAL],
				[self.h_possession, WEIGHT_MATERIAL],
				[self.h_mobility, WEIGHT_MOBILITY],
				[self.h_protects, WEIGHT_PROTECTS]],
			# MATERIAL ONLY
			2: [[self.h_material, WEIGHT_MATERIAL]]
		}
		for evl in FUNCTIONS_SIMPLEHEURISTIC[self.htype]:
			func, weight = evl[0], evl[1]
			self.h += sum([weight[pt]*pn for pt,pn in func(self.c).items()])
		return self.h

def test_simple():
	board = chess.Board()
	color = board.turn

	board.push_san("e4")
	board.push_san("e5")
	board.push_san("d3")
	board.push_san("Nf6")

	csh = ChessSimpleHeuristic(color, board)
	ocsh = ChessSimpleHeuristic(not color, board)
	print(board)
	print(CC_CONV[color], ':', csh.score())
	print(CC_CONV[not color], ':', ocsh.score())

def debug_input(starting_san=[]):
	board = chess.Board()
	color = board.turn
	csh = ChessSimpleHeuristic(color, board)
	ocsh = ChessSimpleHeuristic(not color, board)
	for s in starting_san:
		try:
			board.push_san(s)
			print('Adding move ' + s + '...')
		except Exception as e:
			print(e)
			break
	while True:
		print(board)
		print(CC_CONV[color], 'score =', csh.score())
		print(CC_CONV[not color], 'score =', ocsh.score())
		valid_san = False
		while not valid_san:
			san = input('Move ' + CC_CONV[board.turn] + ':')
			try:
				board.push_san(san)
				valid_san = True
			except Exception as e:
				print(e)
		csh.update(board); ocsh.update(board)

def debug_lm():
	board = chess.Board()
	print(board)
	print(get_legal_moves_better(board,'b1'))
	print(get_legal_moves_better(board,'g8'))
	print(get_legal_moves_better(board,'e2'))
	print(get_legal_moves_better(board,'c7'))

test_simple()