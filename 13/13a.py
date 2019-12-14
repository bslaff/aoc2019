import argparse
import numpy as np
from intcodeComputerNode import IntcodeComputerNode

TILE_EMPTY = 0
TILE_WALL = 1
TILE_BLOCK = 2
TILE_HORZ_PADDLE = 3
TILE_BALL = 4

def get_args():

	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")
	
	return parser.parse_args()


def get_board(args):

	f = open(args.infile, 'r')
	lines = f.readlines()
	f.close()

	lines = [line.strip() for line in lines]
	lines = [line for line in lines if len(line)>0]

	prog = "".join(lines)
	prog = [int(v) for v in prog.split(",")]

	icn = IntcodeComputerNode("A", prog, [])
	icn.run_prog_from_current_state()

	outs = icn.outputs

	idx = 0
	triples = []
	while idx+3 < len(outs):
		triples.append( (int(outs[idx]), int(outs[idx+1]), int(outs[idx+2])) )
		idx += 3

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

def run_game(board_spec):

	X = np.max(board_spec[:,0]+1)
	Y = np.max(board_spec[:,1]+1)

	board = np.zeros(shape=(Y, X))

	for i in range(board_spec.shape[0]):
		x = board_spec[i,0]
		y = board_spec[i,1]
		b = board_spec[i,2]

		board[y,x]=b

	return board

def run_main():

	args = get_args()
	board_spec = get_board(args)
	board = run_game(board_spec)

	num_blocks = np.sum( board.flatten() == TILE_BLOCK )

	print(board)

	print(f"The number of blocks is: {num_blocks}")

	return 0


if __name__=="__main__":

	run_main()