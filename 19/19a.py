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


def run_main():

	args = get_args()
	prog = get_prog(args)

	icn = IntcodeComputerNode("ENIAC", prog, [])

	XX = 50
	YY = 50
	arr = np.zeros(shape=(XX,YY))

	out_ptr=0
	for y in range(YY):
		for x in range(XX):
			# icn.run_prog_from_current_state()
			# print(icn.outputs)
			icn.reset()
			icn.inputs = [y, x]
			# print(f"Running with inputs: {icn.inputs}")
			icn.run_prog_from_current_state()
			# print(f"All outputs: {icn.outputs}")
			# print(f"Exit status: {icn.has_exited}")
			arr[y,x] = icn.outputs[out_ptr]
			# exit()
			# out_ptr += 1

	# print(arr)
	# exit()

	for y in range(YY):
		row = "".join([str(int(v)) for v in arr[y,:]])
		# print(row)
		row = row.replace('1','#').replace('0','.')
		print(row)

	total = np.sum(arr.flatten())

	print(f"Total number of affected spots: {total}")

	return 0

def debug(s):
	print(s)
	return None

if __name__=="__main__":

	run_main()