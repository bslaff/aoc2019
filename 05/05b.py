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

	print("SQAWK!!")
	return False


def get_output(prog, INPUT_VAL):

	OUTPUTS = []

	i=0
	while(True):
		print(f"I AM CURRENTLY: {i}")
		opcode = prog[i]

		if opcode==99:
			print(f"I AM EXITING NOW.")
			break

		(operation, modes) = decode_opcode(opcode)

		if operation==1: # add
			val1 = get_param_value(prog, i+1, modes[2])
			val2 = get_param_value(prog, i+2, modes[1])
			dest = prog[i+3]
			print(f"Add {val1} to {val2} and store at {dest}")
			prog[dest] = val1 + val2
			i += 4

		elif operation==2: # multiply
			val1 = get_param_value(prog, i+1, modes[2])
			val2 = get_param_value(prog, i+2, modes[1])
			dest = prog[i+3]
			print(f"Multiply {val1} to {val2} and store at {dest}")
			prog[dest] = val1 * val2
			i += 4

		elif operation==3:
			# save_input
			dest = prog[i+1]
			print(f"Store input value {INPUT_VAL} at {dest}")
			prog[dest] = INPUT_VAL
			i += 2

		elif operation==4: # output
			# src_addr = prog[i+1]
			# output_val = prog[src_addr]
			output_val = get_param_value(prog, i+1, modes[0])
			print(f"Output {output_val}.")
			OUTPUTS.append(output_val)
			i += 2

		elif operation==5: # jump if true
			val1 = get_param_value(prog, i+1, modes[1])
			val2 = get_param_value(prog, i+2, modes[0])
			if val1 != 0:
				# print("HERE111111")
				print(f"Jump from {i} to {val2}.")
				i = val2
			else:
				print(f"DO NOT jump from {i} to {val2}.")
				i += 3

		elif operation==6: # jump if false
			val1 = get_param_value(prog, i+1, modes[1])
			val2 = get_param_value(prog, i+2, modes[0])
			if val1 == 0:
				print(f"Jump from {i} to {val2}.")
				i = val2
			else:
				print(f"DO NOT jump from {i} to {val2}.")
				i += 3

		elif operation==7: # less than
			val1 = get_param_value(prog, i+1, modes[2])
			val2 = get_param_value(prog, i+2, modes[1])
			dest = prog[i+3]
			if val1 < val2:
				print(f"Since {val1} < {val2}, store 1 at {dest}.")
				prog[dest] = 1
			else:
				print(f"Since {val1} >= {val2}, store 0 at {dest}.")
				prog[dest] = 0
			i += 4

		elif operation==8: # equals
			val1 = get_param_value(prog, i+1, modes[2])
			val2 = get_param_value(prog, i+2, modes[1])
			dest = prog[i+3]
			if val1 == val2:
				print(f"Store 1 at {dest}.")
				prog[dest] = 1
			else:
				print(f"Store 0 at {dest}.")
				prog[dest] = 0
			i += 4

		else:
			print("SQUAWK")

	diagnostic_code = OUTPUTS[-1]
	OTHER_OUTPUTS = OUTPUTS[:-1]
	num_failed = sum([v!=0 for v in OTHER_OUTPUTS])

	print("All outputs except the final: "+str(OTHER_OUTPUTS))

	# print("%i of %i tests failed"%(num_failed, len(OTHER_OUTPUTS)))

	print("The final output is: %i"%(diagnostic_code))

	return diagnostic_code


def run_main():

	args = get_args()
	prog = get_prog(args)

	INPUT_VAL = int(args.input_val)

	get_output(prog, INPUT_VAL)

	return 0


if __name__=='__main__':

	run_main()
