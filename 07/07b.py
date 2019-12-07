import numpy as np
import argparse
import itertools
from amplifier import Amplifier


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


def amp_wrapper(prog):

	highest = -np.inf
	best = None
	exited=[False]*5

	amp_A=Amplifier("A", prog.copy(), [].copy())
	amp_B=Amplifier("B", prog.copy(), [].copy())
	amp_C=Amplifier("C", prog.copy(), [].copy())
	amp_D=Amplifier("D", prog.copy(), [].copy())
	amp_E=Amplifier("E", prog.copy(), [].copy())

	for phase in list(itertools.permutations(list(range(5,10)))):

		[a, b, c, d, e] = phase

		amp_A.inputs.append(a)
		amp_B.inputs.append(b)
		amp_C.inputs.append(c)
		amp_D.inputs.append(d)
		amp_E.inputs.append(e)

		exited=[False]*5
		e_out=0 # initial input
		loopcount = 0

		# debug(f"\nPhase input: {phase}\n")

		while(True):

			amp_A.inputs.append(e_out)
			amp_A.run_prog_from_current_state()
			a_out = amp_A.outputs[-1]

			amp_B.inputs.append(a_out)
			amp_B.run_prog_from_current_state()
			b_out = amp_B.outputs[-1]

			amp_C.inputs.append(b_out)
			amp_C.run_prog_from_current_state()
			c_out = amp_C.outputs[-1]

			amp_D.inputs.append(c_out)
			amp_D.run_prog_from_current_state()
			d_out = amp_D.outputs[-1]

			amp_E.inputs.append(d_out)
			amp_E.run_prog_from_current_state()
			e_out = amp_E.outputs[-1]

			if amp_E.has_exited:
				break

		thruster_signal = e_out

		if highest < thruster_signal:

			highest = thruster_signal
			best_phases = [a, b, c, d, e].copy()

		amp_A.reset()
		amp_B.reset()
		amp_C.reset()
		amp_D.reset()
		amp_E.reset()

	print("BEST PHASES: "+str(best_phases))
	print("HIGHEST THRUSTER SIGNAL: "+str(highest))


def debug(x):

	# print(x)
	return 0

def run_main():

	args = get_args()
	prog = get_prog(args)

	amp_wrapper(prog)

	return 0


if __name__=='__main__':

	run_main()
