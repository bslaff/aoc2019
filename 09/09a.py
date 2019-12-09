import numpy as np
import argparse
import itertools
from intcodeComputerNode import IntcodeComputerNode


def get_args():

	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")
	# parser.add_argument("inputs", type=int, nargs='*', help="Input values for INTCODE program")

	return parser.parse_args()


def get_prog(args):

	f = open(args.infile, 'r')
	prog = f.readlines()
	f.close()

	prog = "".join(prog)
	prog = prog.strip().replace("\n","").replace("\r","").replace(" ","")

	# debug("Original is: %s"%(prog))

	prog = prog.split(",")
	prog = [int(v) for v in prog]

	return(prog)


def debug(x):

	# print(x)
	return 0

def run_main():

	args = get_args()
	prog = get_prog(args)

	inputs=[1]
	icn = IntcodeComputerNode("A", prog, inputs)
	icn.run_prog_from_current_state()

	print(icn.outputs)

	return 0


if __name__=='__main__':

	run_main()
