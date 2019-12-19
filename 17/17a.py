import argparse
import numpy as np
from intcodeComputerNode import IntcodeComputerNode

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

	return prog


def disp_board(board):

	for i in range(board.shape[0]):
		print("".join(board[i,:]))

	return None

def is_crossing(arr, y, x):

	conditions=[ 
	arr[y,x]!='.',
	arr[y-1,x]!='.',
	arr[y+1,x]!='.',
	arr[y,x-1]!='.',
	arr[y,x+1]!='.'
	]

	return all(conditions)


def run_main():

	args = get_args()
	prog = get_prog(args)

	icn = IntcodeComputerNode("A", prog, [])
	icn.run_prog_from_current_state()
	debug( ''.join([chr(v) for v in icn.outputs]) )

	s = ''.join([chr(v) for v in icn.outputs])
	arr = [v for v in s.split('\n') if len(v.strip())>0]

	arr = np.asarray([list(s) for s in arr])
	disp_board(arr)
	debug(arr.shape)

	XX = range(1,(arr.shape[1]-1))
	YY = range(1,(arr.shape[0]-1))

	intersections = []

	for y in YY:
		for x in XX:
			if is_crossing(arr, y, x):
				intersections.append((x, y))

	total=0
	params=[v[0]*v[1] for v in intersections]
	total=sum(params)

	print(f"intersections: {intersections}")
	print(f"{len(intersections)} intersections")
	print(f"parameters: {params}")
	print(f"{len(params)} parameters")
	print(f"The total is {total}")
	return 0

def debug(s):
	print(s)
	return None

if __name__=="__main__":

	run_main()