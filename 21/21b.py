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

	# Unlike in part 1 we might now have enough information to know what to do each time.
	# For example consider:
	# ###.#.#...#
	# ###.#...#.#
	# Now that we can see 9 tiles ahead, we know in part 1 we have to wait to jump, and in 2 we can't wait.
	# Now how can we translate this into spring code. Well, start with logic.

	# if 9 ahead is space, cant jump at 5
	# if 8 ahead is space, cant jump at 4
	# so, don't want to land at 4 unless there is a good jump after:
	# land at 4 if 4 hull AND: 
		# 3 empty, AND
		# 8 hull, OR
		# 5 hull AND (9 hull OR (6 hull and 7 hull))
		# OR 1 empty (no matter what)
	# eh still not perfect but better?

	# ((2 space and 5 space and 1 hull) OR...: NOT B T, NOT E J, AND J T, AND A T # always avoid a suicide jump next step at 1

	# 6 hull and 7 hull: NOT F J, NOT J J, AND G J # result is in J
	# 9 hull OR that: OR I J # result is in J
	# 5 hull AND that: AND E J # result is in J
	# 8 hull OR that: OR H J # result in J
	# 4 hull AND that: AND D J

	# OR T J # finished OR from the very first step

	# 1 empty OR that: NOT A T, OR T J # always jump if we're about to die

	# that is 14.

	# ss = ["NOT F J\n","NOT J J\n", "AND G J\n",
	# "OR I J\n", 
	# "AND E J\n",
	# "OR H J\n",
	# "NOT C T\n", "AND T J\n",
	# "AND D J\n",
	# "NOT A T\n", "OR T J\n", "RUN\n"]

	# ss = ["NOT B T\n","NOT E J\n", "AND J T\n", "AND A T\n",

	# "NOT F J\n", "NOT J J\n", "AND G J\n", 
	# "OR I J\n",
	# "AND E J\n",
	# "OR H J\n",
	# "AND D J\n",

	# "OR T J\n",

	# "NOT A T\n", "OR T J\n", "RUN\n"]

	# ss = [

	# "NOT F J\n", "NOT J J\n", 	# (((6 hull
	# "OR I J\n", 				# or 9 hull)
	# "AND E J\n",				# and 5 hull)
	# "OR H J\n",					# or 8 hull)
	# "AND D J\n",				# and 4 hull
	# "NOT C T\n", "AND T J\n",	# and 3 space

	# "NOT B T\n", 
	# "AND E T\n", "NOT T T\n",
	# "AND A J\n",

	# "NOT A T\n", "OR T J\n", "RUN\n"]

	###############################################

	#### ALRIGHT LOTS OF FALSE STARTS ABOVE but finally got something working:

	ss = ["NOT B T\n","NOT E J\n", "AND J T\n", "AND A T\n", # (if 2 space and 5 space and 1 hull, 
	"NOT C J\n", "OR J T\n", # OR 3 space: TRUE -> T)

	"NOT E J\n", "NOT J J\n",		# (5 hull
	"OR H J\n",					# or 8 hull)
	"AND D J\n",				# and 4 hull: TRUE -> J

	"AND T J\n"					# T and J -> J

	"NOT A T\n", "OR T J\n", "RUN\n"] # if 1 is space or J: J true

	# In english:
	# Jump if:
		# it would be a safe-ish jump (4 is hull AND 5 or 8 is hull), AND either
			# the next step leads to a suicide jump (2 space, 5 space, 1 hull) OR 
			# 3 is a space
		# OR: 1 is a space (have to jump)

	ss = [ord(v) for v in "".join(ss)]
	# print(ss)
	icn.inputs = ss
	icn.run_prog_from_current_state()
	outs = icn.outputs

	print(f"The outputs are: {outs}")

	if outs[-1]<=127:
		tumbled = "".join([chr(v) for v in outs])
		print(tumbled)

	### Output a bunch of ascii-range integers and then a single giant integer which worked.
	### Cool. Not bad heuristic-finding exercise. Wonder if there was a more "code" way to do it.
	### Some reddit solutions talk about SAT machines which could be entertaining.

	return 0

def debug(s):
	print(s)
	return None

if __name__=="__main__":

	run_main()