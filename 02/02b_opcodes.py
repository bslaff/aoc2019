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


def get_output(prog):

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

	return prog[0]


def run_main():

	args = get_args()
	orig_prog = get_prog(args)

	for noun in range(100):
		for verb in range(100):

			prog = orig_prog.copy()
			prog[1] = noun
			prog[2] = verb
			output = get_output(prog)

			if output==19690720:
				print("Answer: noun=%i, verb=%i"%(noun, verb))
				print("Final answer: %i"%(100*noun+verb))
				return 100*noun+verb

	print("SQUAWK")
	return -1


if __name__=='__main__':

	run_main()
