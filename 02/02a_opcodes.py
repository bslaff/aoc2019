import numpy as np
import argparse


def get_args():
	
	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")
	
	return parser.parse_args()


def get_prog(args):

	f = open(args.infile, 'r')
	prog = f.readlines()
	f.close()

	prog = "".join(prog)
	prog = prog.strip().replace("\n","").replace("\r","").replace(" ","")

	print("Original is: %s"%(prog))

	prog = prog.split(",")
	prog = [int(v) for v in prog]

	return(prog)


def run_main():

	args = get_args()
	prog = get_prog(args)

	i=0
	while(True):
		opcode = prog[i]

		if opcode==99:
			break

		idx_1 = prog[i+1]
		idx_2 = prog[i+2]
		dest = prog[i+3]

		if opcode==1:
			prog[dest] = prog[idx_1] + prog[idx_2]

		elif opcode==2:
			prog[dest] = prog[idx_1] * prog[idx_2]

		else:
			print("SQUAWK")

		i += 4

	final_state = ",".join([str(v) for v in prog])

	print("The result is: %s"%(final_state))
	return(final_state)


if __name__=='__main__':

	run_main()
