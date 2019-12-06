import numpy as np
import argparse


def get_args():

	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")
	parser.add_argument("input_val", type=int, help="Input value for INTCODE program")

	return parser.parse_args()


def get_prog(args):

	f = open(args.infile, 'r')
	prog = f.readlines()
	f.close()

	prog = "".join(prog)
	prog = prog.strip().replace("\n","").replace("\r","").replace(" ","")

	# print("Original is: %s"%(prog))

	prog = prog.split(",")
	prog = [int(v) for v in prog]

	return(prog)

def decode_opcode(opcode):

	opstr = str(opcode)
	# print(opstr)
	
	if len(opstr)<2:
		opstr="0"+opstr

	operation = int(opstr[-2:])

	if operation in [1, 2]: #add, multiply
		while len(opstr)<5:
			opstr="0"+opstr

	if operation in [3, 4]: #store input, output
		while len(opstr)<3:
			opstr="0"+opstr

	modes=[int(v) for v in list(opstr[:-2])]
	return(operation, modes)

def get_param_value(prog, p_idx, mval):

	if mval==0: #parameter mode
		return prog[ prog[p_idx] ]
	elif mval==1: #immediate mode
		return prog[ p_idx ]

	print("SQAWK!!")
	return False


def get_output(prog, INPUT_VAL):

	OUTPUTS = []

	i=0
	while(True):
		opcode = prog[i]

		if opcode==99:
			break

		(operation, modes) = decode_opcode(opcode)

		if operation==1: # add
			val1 = get_param_value(prog, i+1, modes[2])
			val2 = get_param_value(prog, i+2, modes[1])
			dest = prog[i+3]
			# print(f"Add {val1} to {val2} and store at {dest}\n")
			prog[dest] = val1 + val2
			i += 4

		elif operation==2: # multiply
			val1 = get_param_value(prog, i+1, modes[2])
			val2 = get_param_value(prog, i+2, modes[1])
			dest = prog[i+3]
			# print(f"Multiply {val1} to {val2} and store at {dest}\n")
			prog[dest] = val1 * val2
			i += 4

		elif operation==3:
			# save_input
			dest = prog[i+1]
			# print(f"Store input value {INPUT_VAL} at {dest}\n")
			prog[dest] = INPUT_VAL
			i += 2

		elif operation==4: # output
			# src_addr = prog[i+1]
			# output_val = prog[src_addr]
			output_val = get_param_value(prog, i+1, modes[0])
			# print(f"Output {output_val}.\n")
			OUTPUTS.append(output_val)
			i += 2

		else:
			print("SQUAWK")

	diagnostic_code = OUTPUTS[-1]
	OTHER_OUTPUTS = OUTPUTS[:-1]
	num_failed = sum([v!=0 for v in OTHER_OUTPUTS])

	print("Test results: "+str(OTHER_OUTPUTS))

	print("%i of %i tests failed"%(num_failed, len(OTHER_OUTPUTS)))

	print("The diagnostic code is: %i"%(diagnostic_code))

	return diagnostic_code


def run_main():

	args = get_args()
	prog = get_prog(args)

	INPUT_VAL = int(args.input_val)

	get_output(prog, INPUT_VAL)

	return 0


if __name__=='__main__':

	run_main()
