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

def run_with_inputs_get_output(icn, inputs):

		icn.reset()
		icn.inputs = inputs
		icn.run_prog_from_current_state()
		v = icn.outputs[0]

		return v


def run_main():

	args = get_args()
	prog = get_prog(args)

	icn = IntcodeComputerNode("ENIAC", prog, [])

	# record_d = dict()

	SQ_SZ=100

	y=15 # initialize
	while(True):
		
		print(f"y is {y}")

		# binary search for biggest column index for which the beam takes effect (output 1)
		min_x = y
		max_x = 10*y
		x = y
		v = run_with_inputs_get_output(icn, [y, x])

		while(True):

			if v==1:
				min_x = x
				last_x = x
				x = int( (x+max_x)/2 )
			elif v==0:
				max_x = x
				last_x = x
				x = int( (x+min_x)/2 )

			if abs(x-last_x)==0:
				break

		# make sure
		while run_with_inputs_get_output(icn, [y, x])==0:
			x -= 1

		# really got x now. now test:
		pros_y = y + (SQ_SZ-1)
		pros_x = x - (SQ_SZ-1)

		print(f"for y={y}, testing pros_x, pros_y = {pros_x}, {pros_y}")

		if pros_x < 0:
			pass
		else:
			v = run_with_inputs_get_output(icn, [pros_y, pros_x])
			if v==1:
				final_y = y
				final_x = pros_x
				
				verdict = int( 10000*final_x+final_y )
				print(f"final x, y: {final_x}, {final_y}")
				print(f"Verdict is {verdict}")
				exit()

		y += 1

		#Ultimately got:
		# y is 948
		# for y=948, testing pros_x, pros_y = 761, 1047
		# final x, y: 761, 948
		# Verdict is 7610948. WRONG, too low.
		# Just checking do we have x, y backwards: verdict would be: 9480761
		# Yes! that was it. Not sure how I should have known that, but there we go.

	return 0

def debug(s):
	print(s)
	return None

if __name__=="__main__":

	run_main()