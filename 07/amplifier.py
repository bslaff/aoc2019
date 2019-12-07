class Amplifier:

	def __init__(self, name, prog, inputs):

		self.name=name
		self.instr_ptr=0
		self.input_ptr=0
		self.prog = prog.copy()
		self.original_prog = prog.copy()
		self.inputs = inputs.copy()
		self.original_inputs = inputs.copy()
		self.outputs = [].copy()
		self.is_halted = True
		self.has_exited = False

	def reset(self):

		self.instr_ptr=0
		self.input_ptr=0
		self.inputs = self.original_inputs.copy()
		self.outputs = [].copy()
		self.is_halted = True
		self.has_exited = False
		self.prog = self.original_prog.copy()

	def debug(self, x):

		# print(f"{self.name}: {x}")
		return 0

	def run_prog_from_current_state(self):

		self.is_halted = False

		NUM_INPUTS=len(self.inputs)

		while(True):
			self.debug(f"I AM CURRENTLY: {self.instr_ptr}")
			opcode = self.prog[self.instr_ptr]

			if opcode==99:
				self.debug(f"I AM EXITING NOW.")
				self.has_exited = True
				break

			(operation, modes) = decode_opcode(opcode)

			if operation==1: # add
				val1 = get_param_value(self.prog, self.instr_ptr+1, modes[2])
				val2 = get_param_value(self.prog, self.instr_ptr+2, modes[1])
				dest = self.prog[self.instr_ptr+3]
				self.debug(f"Add {val1} to {val2} and store at {dest}")
				self.prog[dest] = val1 + val2
				self.instr_ptr += 4

			elif operation==2: # multiply
				val1 = get_param_value(self.prog, self.instr_ptr+1, modes[2])
				val2 = get_param_value(self.prog, self.instr_ptr+2, modes[1])
				dest = self.prog[self.instr_ptr+3]
				self.debug(f"Multiply {val1} to {val2} and store at {dest}")
				self.prog[dest] = val1 * val2
				self.instr_ptr += 4

			elif operation==3:
				# save_input
				dest = self.prog[self.instr_ptr+1]

				if self.input_ptr < NUM_INPUTS:
					input_val = self.inputs[self.input_ptr]
					self.input_ptr += 1
				else:
					# Not enough inputs! halt and wait for next input
					self.debug(f"Received 'input' command, but there are no inputs available! Halting now.")
					self.debug(f"My inputs are: {self.inputs}")
					self.debug(f"My outputs are: {self.outputs}")
					self.is_halted = True
					break

				self.debug(f"Store input value {input_val} at {dest}")
				self.prog[dest] = input_val
				self.instr_ptr += 2

			elif operation==4: # output
				output_val = get_param_value(self.prog, self.instr_ptr+1, modes[0])
				self.debug(f"Output {output_val}.")
				self.outputs.append(output_val)
				self.instr_ptr += 2

			elif operation==5: # jump if true
				val1 = get_param_value(self.prog, self.instr_ptr+1, modes[1])
				val2 = get_param_value(self.prog, self.instr_ptr+2, modes[0])
				if val1 != 0:
					self.debug(f"Jump from {self.instr_ptr} to {val2}.")
					self.instr_ptr = val2
				else:
					self.debug(f"DO NOT jump from {self.instr_ptr} to {val2}.")
					self.instr_ptr += 3

			elif operation==6: # jump if false
				val1 = get_param_value(self.prog, self.instr_ptr+1, modes[1])
				val2 = get_param_value(self.prog, self.instr_ptr+2, modes[0])
				if val1 == 0:
					self.debug(f"Jump from {self.instr_ptr} to {val2}.")
					self.instr_ptr = val2
				else:
					self.debug(f"DO NOT jump from {self.instr_ptr} to {val2}.")
					self.instr_ptr += 3

			elif operation==7: # less than
				val1 = get_param_value(self.prog, self.instr_ptr+1, modes[2])
				val2 = get_param_value(self.prog, self.instr_ptr+2, modes[1])
				dest = self.prog[self.instr_ptr+3]
				if val1 < val2:
					self.debug(f"Since {val1} < {val2}, store 1 at {dest}.")
					self.prog[dest] = 1
				else:
					self.debug(f"Since {val1} >= {val2}, store 0 at {dest}.")
					self.prog[dest] = 0
				self.instr_ptr += 4

			elif operation==8: # equals
				val1 = get_param_value(self.prog, self.instr_ptr+1, modes[2])
				val2 = get_param_value(self.prog, self.instr_ptr+2, modes[1])
				dest = self.prog[self.instr_ptr+3]
				if val1 == val2:
					self.debug(f"Store 1 at {dest}.")
					self.prog[dest] = 1
				else:
					self.debug(f"Store 0 at {dest}.")
					self.prog[dest] = 0
				self.instr_ptr += 4

			else:
				self.debug("SQUAWK")

		return 0


def decode_opcode(opcode):

	opstr = str(opcode)
	# self.debug(opstr)
	
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