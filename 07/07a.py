import numpy as np
import argparse
import itertools


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

def decode_opcode(opcode):

	opstr = str(opcode)
	# debug(opstr)
	
	if len(opstr)<2:
		opstr="0"+opstr

	operation = int(opstr[-2:])

	if operation in [1, 2, 7, 8]: #add, multiply
		while len(opstr)<5:
			opstr="0"+opstr

	elif operation in [5, 6]: #store input, output
		while len(opstr)<4:
			opstr="0"+opstr

	elif operation in [3, 4]: #store input, output
		while len(opstr)<3:
			opstr="0"+opstr

	modes=[int(v) for v in list(opstr[:-2])]
	return(operation, modes)

def get_param_value(prog, p_idx, mval):

	if mval==0: #parameter mode
		return prog[ prog[p_idx] ]
	elif mval==1: #immediate mode
		return prog[ p_idx ]

	debug("SQAWK!!")
	return False


def get_output(prog, INPUTS):

	OUTPUTS = []

	INPUT_CTR=0
	NUM_INPUTS=len(INPUTS)

	i=0
	while(True):
		debug(f"I AM CURRENTLY: {i}")
		opcode = prog[i]

		if opcode==99:
			debug(f"I AM EXITING NOW.")
			break

		(operation, modes) = decode_opcode(opcode)

		if operation==1: # add
			val1 = get_param_value(prog, i+1, modes[2])
			val2 = get_param_value(prog, i+2, modes[1])
			dest = prog[i+3]
			debug(f"Add {val1} to {val2} and store at {dest}")
			prog[dest] = val1 + val2
			i += 4

		elif operation==2: # multiply
			val1 = get_param_value(prog, i+1, modes[2])
			val2 = get_param_value(prog, i+2, modes[1])
			dest = prog[i+3]
			debug(f"Multiply {val1} to {val2} and store at {dest}")
			prog[dest] = val1 * val2
			i += 4

		elif operation==3:
			# save_input
			dest = prog[i+1]

			if INPUT_CTR < NUM_INPUTS:
				input_val = INPUTS[INPUT_CTR]
				INPUT_CTR += 1
			else:
				debug("NOT ENOUGH INPUTS!")
				exit()

			debug(f"Store input value {input_val} at {dest}")
			prog[dest] = input_val
			i += 2

		elif operation==4: # output
			# src_addr = prog[i+1]
			# output_val = prog[src_addr]
			output_val = get_param_value(prog, i+1, modes[0])
			debug(f"Output {output_val}.")
			OUTPUTS.append(output_val)
			i += 2

		elif operation==5: # jump if true
			val1 = get_param_value(prog, i+1, modes[1])
			val2 = get_param_value(prog, i+2, modes[0])
			if val1 != 0:
				# debug("HERE111111")
				debug(f"Jump from {i} to {val2}.")
				i = val2
			else:
				debug(f"DO NOT jump from {i} to {val2}.")
				i += 3

		elif operation==6: # jump if false
			val1 = get_param_value(prog, i+1, modes[1])
			val2 = get_param_value(prog, i+2, modes[0])
			if val1 == 0:
				debug(f"Jump from {i} to {val2}.")
				i = val2
			else:
				debug(f"DO NOT jump from {i} to {val2}.")
				i += 3

		elif operation==7: # less than
			val1 = get_param_value(prog, i+1, modes[2])
			val2 = get_param_value(prog, i+2, modes[1])
			dest = prog[i+3]
			if val1 < val2:
				debug(f"Since {val1} < {val2}, store 1 at {dest}.")
				prog[dest] = 1
			else:
				debug(f"Since {val1} >= {val2}, store 0 at {dest}.")
				prog[dest] = 0
			i += 4

		elif operation==8: # equals
			val1 = get_param_value(prog, i+1, modes[2])
			val2 = get_param_value(prog, i+2, modes[1])
			dest = prog[i+3]
			if val1 == val2:
				debug(f"Store 1 at {dest}.")
				prog[dest] = 1
			else:
				debug(f"Store 0 at {dest}.")
				prog[dest] = 0
			i += 4

		else:
			debug("SQUAWK")

	diagnostic_code = OUTPUTS[-1]
	OTHER_OUTPUTS = OUTPUTS[:-1]
	num_failed = sum([v!=0 for v in OTHER_OUTPUTS])

	debug("All outputs except the final: "+str(OTHER_OUTPUTS))

	# debug("%i of %i tests failed"%(num_failed, len(OTHER_OUTPUTS)))

	debug("The final output is: %i"%(diagnostic_code))

	return diagnostic_code


def amp_wrapper(prog):

	highest = -np.inf
	best = None

	for [a, b, c, d, e] in list(itertools.permutations(list(range(5)))):

		a_out = get_output(prog, [a, 0])
		b_out = get_output(prog, [b, a_out])
		c_out = get_output(prog, [c, b_out])
		d_out = get_output(prog, [d, c_out])
		e_out = get_output(prog, [e, d_out])

		thruster_signal = e_out

		if highest < thruster_signal:

			highest = thruster_signal
			best_phases = [a, b, c, d, e]

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
