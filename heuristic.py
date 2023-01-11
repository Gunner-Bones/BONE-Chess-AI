import chess
import random

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

def move_to_san(board, move, long=False):
	# fixed pychess board.san() function because its bugged and always asserts, you're welcome
	# Null move.
	if not move:
		return "--"
	# Drops.
	if move.drop:
		san = ""
		if move.drop != chess.PAWN:
			san = chess.piece_symbol(move.drop).upper()
		san += "@" + chess.SQUARE_NAMES[move.to_square]
		return san
	# Castling.
	if board.is_castling(move):
		if chess.square_file(move.to_square) < chess.square_file(move.from_square):
			return "O-O-O"
		else:
			return "O-O"
	piece_type = get_piece_type(board, move)
	capture = board.is_capture(move)
	if piece_type == chess.PAWN:
		san = ""
	else:
		san = chess.piece_symbol(piece_type).upper()
	if long:
		san += chess.SQUARE_NAMES[move.from_square]
	elif piece_type != chess.PAWN:
		# Get ambiguous move candidates.
		# Relevant candidates: not exactly the current move,
		# but to the same square.
		others = 0
		from_mask = board.pieces_mask(piece_type, board.turn)
		from_mask &= ~chess.BB_SQUARES[move.from_square]
		to_mask = chess.BB_SQUARES[move.to_square]
		for candidate in board.generate_legal_moves(from_mask, to_mask):
			others |= chess.BB_SQUARES[candidate.from_square]
		# Disambiguate.
		if others:
			row, column = False, False
			if others & chess.BB_RANKS[chess.square_rank(move.from_square)]:
				column = True
			if others & chess.BB_FILES[chess.square_file(move.from_square)]:
				row = True
			else:
				column = True
			if column:
				san += chess.FILE_NAMES[chess.square_file(move.from_square)]
			if row:
				san += chess.RANK_NAMES[chess.square_rank(move.from_square)]
	elif capture:
		san += chess.FILE_NAMES[chess.square_file(move.from_square)]
	# Captures.
	if capture:
		san += "x"
	elif long:
		san += "-"
	# Destination square.
	san += chess.SQUARE_NAMES[move.to_square]
	# Promotion.
	if move.promotion:
		san += "=" + chess.piece_symbol(move.promotion).upper()
	return san

def global_is_legal(board, color, move):
	il = None
	if board.turn != color:
		board.push(chess.Move.from_uci("0000"))
		il = board.is_legal(move)
		board.pop()
	else:
		il = board.is_legal(move)
	return il

def get_piece_type(board, move):
	# checks both positions depending on when the piece was moved
	muci = move.uci()
	if len(muci) == 5:
		muci = muci[:4]
	bpa = board.piece_at(chess.parse_square(muci[:2]))
	if not bpa:
		bpa = board.piece_at(chess.parse_square(muci[2:]))
	return bpa.piece_type

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

def move_gives_checkmate(board, move):
	board.push(move)
	try:
		return board.is_checkmate()
	finally:
		board.pop()

def piece_gives_checkmate(board, at):
	moves = get_legal_moves_better(board, at)
	for m in moves:
		move = chess.Move.from_uci(m)
		if move_gives_checkmate(board, move):
			return True
	return False

def move_to_san_better(board, move):
	#print('inc',move)
	"""rewrote a san() function because chess.board.san() is almost entirely broken
	   we also ain't doin no drops or uci tomfoolery"""
	# Null
	if not move:
		return '--'
	# Check stupid board turn based bs
	deleted_move = None
	if not get_piece_type(board, move):
		deleted_move = board.pop()
	else:
		try:
			board.gives_check(move)
		except:
			deleted_move = board.pop()
			if board.peek() == deleted_move:
				board.pop()
	# Castling
	if board.is_castling(move):
		if chess.square_file(move.to_square) < chess.square_file(move.from_square):
			board.push(deleted_move) if deleted_move else None
			return "O-O-O"
		else:
			board.push(deleted_move) if deleted_move else None
			return "O-O"
	# Normal move
	pt = get_piece_type(board, move)
	spt = CPT_CONV[pt].upper() if pt != chess.PAWN else ''
	spos = chess.square_name(move.to_square)
	san = spt + spos
	# Disambiguous moves
	lm = get_all_legal_moves(board, board.turn)
	same_moves = [m for m in lm if CPT_CONV[get_piece_type(board, chess.Move.from_uci(m))].upper() == spt]
	if len(same_moves) == 2:
		common = same_moves[0][0] if same_moves[0][0] == same_moves[1][0] else same_moves[0][1]
		for sm in same_moves:
			if sm[:2] == spos:
				san = spt + sm[:2].replace(common,'') + spos
				break
	# Capture
	if board.is_capture(move):
		if pt == chess.PAWN:
			san = chess.square_name(move.from_square)[0] + 'x' + spos
		else:
			san = spt + 'x' + spos
	# Promotion
	if move.promotion:
		san += '=' + CPT_CONV[move.promotion].upper()
	# Check
	if board.gives_check(move):
		san += '+'
	# Checkmate
	if piece_gives_checkmate(board, spos):
		san = san.replace('+','') + '#'
	board.push(deleted_move) if deleted_move else None
	return san

def chess_heuristic():
	return {'p': 0, 'r': 0, 'b': 0, 'n': 0, 'q': 0, 'k': 0}

def check_heuristic():
	return {'checkmate': 0, 'check': 0}

# heuristic constants
HEURISTIC_MAX = 50000
WEIGHT_MATERIAL = {
	'p': 100,
	'n': 330,
	'b': 360,
	'r': 500,
	'q': 900,
	'k': 0 # players always have a king unless the game ends
}
WEIGHT_MOBILITY = {
	'p': 20,
	'n': 15,
	'b': 15,
	'r': 12,
	'q': 20,
	'k': 5
}
WEIGHT_PROTECTS = { # should be less than half material weight so capturing is weighted better than attacking
	'p': 25,
	'n': 80,
	'b': 90,
	'r': 120,
	'q': 295,
	'k': 9000
}
VALUE_WEIGHT_GOODATTACK = 2 # enemy piece being attacked isn't protected
VALUE_WEIGHT_FORKINGMULTIPLIER = 3 # forking gives a chance to hang enemy pieces, so it's better than a normal attack
WEIGHT_WINNING = {
	'checkmate': HEURISTIC_MAX,
	'check': int(HEURISTIC_MAX / 1000)
}
VALUE_WEIGHT_CHECKMULTIPLIER = 10 # for every succeeding piece that checks, the check score multiplies by this much

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
		""" Evaluates what pieces can move. """
		score = chess_heuristic()
		for pt in CPT_CONV.keys():
			pts = len(get_type_legal_moves(self.b, color, pt))
			score[CPT_CONV[pt]] += pts
		return score
	def h_protects(self, color):
		""" Evaluates what pieces are protected. """
		score = chess_heuristic()
		pieces = get_color_pieces(self.b, color)
		lm = [m[2:] for m in get_all_pseudo_moves(self.b, color)]
		o_lm = [m[2:] for m in get_all_legal_moves(self.b, not color)]
		for p in pieces.items():
			pos,piece = p[0],p[1]
			if pos in lm and pos in o_lm:
				score[CPT_CONV[piece.piece_type]] += 1
		return score
	def h_attacks(self, color):
		""" Evaluates what pieces are being attacked. Extra points if attacked piece isn't protected. 
			Scoring is inverted, points total towards which enemy pieces are being attacked, not
			which ally pieces are attacking."""
		score = chess_heuristic()
		o_pieces = get_color_pieces(self.b, not color)
		lm = [m[2:] for m in get_all_pseudo_moves(self.b, color)]
		o_lm = [m[2:] for m in get_all_legal_moves(self.b, not color)]
		for op in o_pieces.items():
			opos,opiece = op[0],op[1]
			if opos in lm:
				times = 1
				if opos not in o_lm:
					times *= VALUE_WEIGHT_GOODATTACK
				score[CPT_CONV[opiece.piece_type]] += times
		return score
	def h_forking(self, color):
		""" Evaluates what pieces are being attacked in a fork. Scoring is inverted. """
		score = chess_heuristic()
		o_pieces = get_color_pieces(self.b, not color).items()
		lm = [m[2:] for m in get_all_pseudo_moves(self.b, color)]
		o_lm = [m[2:] for m in get_all_legal_moves(self.b, not color)]
		m_attacks = {}
		for m in lm:
			m_attacks[m] = []
			for op in o_pieces:
				opos,opiece = op[0],op[1]
				if opos == m:
					m_attacks[m].append(opiece)
		m_forks = [[k,v] for k,v in m_attacks if len(v) > 1]
		if m_forks:
			for mf in m_forks:
				forked = mf[1]
				for f in forked:
					score[CPT_CONV[opiece.piece_type]] += VALUE_WEIGHT_FORKINGMULTIPLIER
		return score
	def h_winning(self, color):
		""" Evaluates if you have check or checkmate. Check value is higher if more pieces are checking. """
		score = check_heuristic()
		checkers = list(self.b.checkers())
		if checkers:
			for ck in checkers:
				cks = chess.square_name(chess.Square(ck))
				score['check'] = 1 if not score['check'] else score['check'] * VALUE_WEIGHT_CHECKMULTIPLIER
				if piece_gives_checkmate(self.b, cks):
					score['checkmate'] += 1
					break
		return score
	def h_losing(self, color):
		""" Evaluates if you are in check or checkmate. Check value is higher if more pieces are checking. """
		return self.h_winning(not color)
	def score(self):
		""" Returns the heuristic score. """
		FUNCTIONS_SIMPLEHEURISTIC = {
			# ALL
			1: [[self.h_material, WEIGHT_MATERIAL],
				[self.h_possession, WEIGHT_MATERIAL],
				[self.h_mobility, WEIGHT_MOBILITY],
				[self.h_protects, WEIGHT_PROTECTS],
				[self.h_attacks, WEIGHT_PROTECTS],
				[self.h_forking, WEIGHT_PROTECTS],
				[self.h_winning, WEIGHT_WINNING],
				[self.h_losing, WEIGHT_WINNING]],
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
	print(CC_CONV[not color], ':', -ocsh.score())

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
		print(CC_CONV[not color], 'score =', -ocsh.score())
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
	board.push_san('e4')
	print(move_to_san_better(board,board.peek()))
	board.push_san('e5')
	print(move_to_san_better(board,board.peek()))
	board.push_san('Nc3')
	print(move_to_san_better(board,board.peek()))

def debug_checkmate():
	board = chess.Board(fen='4k3/7Q/8/6B1/8/8/8/K7 w - - 0 1')
	move = chess.Move.from_uci('h7e7')
	color = board.turn
	csh = ChessSimpleHeuristic(color, board)
	ocsh = ChessSimpleHeuristic(not color, board)
	print(board)
	print(CC_CONV[color], ':', csh.score())
	print(CC_CONV[not color], ':', -ocsh.score())
	print(piece_gives_checkmate(board, 'h7'))

#debug_checkmate()