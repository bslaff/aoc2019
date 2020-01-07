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

	# I don't think there is a strategy that is guaranteed to win based on what we know
	# For example consider:
	# ###.#.#...#
	# ###.#...#.#
	# In the first case, you have to jump at step 3 or you lose
	# In the second case, you have to jump at step 1 or you lose
	# But it looks the same from the beginning. No way to tell them apart.
	# So no strategy is guaranteed to work.
	# A good solution would be something like: figure out rules which allow us to greedily go forward
	# until we have rules that are *good enough* to get us to the end.
	# Or, we can try a heuristic and go from there. Opting for this.

	# So, heuristic strategy: jump if
	### 4 ahead is hull AND 3 ahead is not hull, OR 1 ahead is not hull
	# sure, we can refine from there as long as we take care to visualize the output.

	ss = ["NOT C J\n","AND D J\n", "NOT A T\n", "OR T J\n", "WALK\n"]
	ss = [ord(v) for v in "".join(ss)]
	# print(ss)
	icn.inputs = ss
	icn.run_prog_from_current_state()
	outs = icn.outputs

	print(f"The outputs are: {outs}")
	### Output a bunch of ascii-range integers and then a single giant integer which worked.
	### Great but not the most satisfying I guess?

	return 0

def debug(s):
	print(s)
	return None

if __name__=="__main__":

	run_main()