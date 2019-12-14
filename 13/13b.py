import argparse
import numpy as np
from intcodeComputerNode import IntcodeComputerNode

ball_loc = dict()
paddle = (-1, -1)

def get_args():

	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")
	
	return parser.parse_args()


def get_prog(args):

	f = open(args.infile, 'r')
	lines = f.readlines()
	f.close()

	lines = [line.strip() for line in lines]
	lines = [line for line in lines if len(line)>0]

	prog = "".join(lines)
	prog = [int(v) for v in prog.split(",")]

	## Set mem address to 2 to play for free
	prog[0]=2

	return prog

def output_to_board_spec(outs):

	idx = 0
	triples = []
	while idx+2 < len(outs):
		triples.append( (int(outs[idx]), int(outs[idx+1]), int(outs[idx+2])) )
		idx += 3

	# print(triples)

	L = len(triples)
	board_spec = np.zeros(shape=(L,3), dtype=int)
	for i in range(len(triples)):
		t = triples[i]
		x = t[0] # offset from left
		y = t[1] # offset from top
		b = t[2] # board element
		board_spec[i,0]=x
		board_spec[i,1]=y
		board_spec[i,2]=b

	return(board_spec)

def init_board(board_spec):

	X = np.max(board_spec[:,0]+1)
	Y = np.max(board_spec[:,1]+1)

	board = np.zeros(shape=(Y, X))

	update_board(board_spec, board)

	return board

def segment_display(score):

	print(f"SEGMENT DISPLAY: {score}")
	return None

def update_board(board_spec, board):

	global ball_loc
	global paddle

	# print(f"Updating board:")
	# print(board_spec)

	for i in range(board_spec.shape[0]):
		# print(board_spec[i,:])
		x = board_spec[i,0]
		y = board_spec[i,1]
		b = board_spec[i,2]

		if x==-1 and y==0:
			segment_display(b)
		else:
			board[y,x]=b

		if (x, y)==ball_loc["current"]:
			# print(f"[{get_char(b)}] drawn at ball location {(x, y)}")
			pass

		if b==4:
			# print(f"Ball drawn at {x}, {y}.")
			ball_loc["previous"] = ball_loc["current"]
			ball_loc["current"] = (x, y)

		if b==3:
			paddle = (x, y)

	return None

def get_char(v):

	if v==0: # empty
		return ' '
	elif v==1: # wall
		return '|'
	elif v==2: # block
		return '+'
	elif v==3: # horizontal paddle
		return '-'
	elif v==4: # ball
		return 'O'

	# TILE_EMPTY = 0
	# TILE_WALL = 1
	# TILE_BLOCK = 2
	# TILE_HORZ_PADDLE = 3
	# TILE_BALL = 4
	print("SQUAWK")
	return 'S' # hopefully never

def disp_board(board):

	(Y, X) = board.shape

	bb = board.flatten()
	bb = [get_char(v) for v in bb]
	bb = np.asarray(bb).reshape(board.shape)

	for i in range(bb.shape[0]):
		print("".join(bb[i,:]))

	return None

def get_process_user_input():

	valid = set([-1, 0, 1])
	v = -2
	first = True

	while v not in valid:
		if not first:
			print(f"Invalid input: {v}")
		first=False
		v = input('--> ')
		try:
			v = int(v.strip())
		except:
			continue

	return v

def get_auto_input():

	global ball_loc
	global paddle

	paddle_x = paddle[0]
	paddle_y = paddle[1]

	ball_x = ball_loc["current"][0]
	traj = ball_loc["current"][0] - ball_loc["previous"][0]

	if traj == 0:
		# initial ball state
		return 0 # do nothing

	### SPECIAL CASES
	if ball_loc["current"] == (paddle_x, paddle_y-1):
		# if ball is just above the paddle
		return 0

	if ball_loc["current"] == (paddle_x+1, paddle_y-1) and traj < 0:
		# if ball is just above the paddle and to the right, and moving left:
		return 0

	if ball_loc["current"] == (paddle_x-1, paddle_y-1) and traj > 0:
		# if ball is just above the paddle and to the left, and moving right:
		return 0

	### NON-SPECIAL CASES
	if paddle_x > ball_x and traj > 0:
		# paddle is right of the ball, and ball is moving right
		return 0

	if paddle_x > ball_x and traj < 0:
		# we lose?
		return -1

	if paddle_x == ball_x and traj > 0:
		return 1

	if paddle_x == ball_x and traj < 0:
		return -1

	if paddle_x < ball_x and traj > 0:
		# we lose?
		return 1

	if paddle_x < ball_x and traj < 0:
		return 0

	print("SQUAWK!!!")
	return 0


def run_main():

	global ball_loc
	global paddle
	ball_loc["current"] = (-1, -1) # initialize

	args = get_args()
	prog = get_prog(args)

	icn = IntcodeComputerNode("A", prog, [])
	icn.run_prog_from_current_state()

	board_spec = output_to_board_spec(icn.outputs)
	L = len(icn.outputs)

	board = init_board(board_spec)
	ball_loc["previous"] = ball_loc["current"] # initialize "previous"

	while not icn.has_exited:

		# disp_board(board)
		# joystick_instr = get_process_user_input() # too slow!
		joystick_instr = get_auto_input()
		icn.inputs.append(joystick_instr)

		icn.run_prog_from_current_state()

		# print(f"BALL: {ball_loc['current']}, PADDLE: {paddle}")

		board_spec = output_to_board_spec(icn.outputs[L:])
		# print(icn.outputs[L:])
		# print(board_spec)
		L = len(icn.outputs)

		update_board(board_spec, board)

	return 0


if __name__=="__main__":

	run_main()