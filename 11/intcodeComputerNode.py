class IntcodeComputerNode:

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
		self.relative_base = 0

	def reset(self):

		self.instr_ptr=0
		self.input_ptr=0
		self.inputs = self.original_inputs.copy()
		self.outputs = [].copy()
		self.is_halted = True
		self.has_exited = False
		self.prog = self.original_prog.copy()
		self.relative_base = 0

	def debug(self, x):

		# print(f"{self.name}: {x}")
		return 0

	def get_param_addr_value(self, p_idx, mval):

		self.maybe_extend_memory(p_idx)

		if mval==0: #parameter mode
			self.maybe_extend_memory( self.prog[p_idx] )
			addr=self.prog[p_idx]
			val=self.prog[ self.prog[p_idx] ]
		elif mval==1: #immediate mode
			addr=p_idx
			val=self.prog[p_idx]
		elif mval==2:
			self.maybe_extend_memory( self.prog[p_idx] + self.relative_base )
			addr=self.prog[p_idx] + self.relative_base
			val=self.prog[ self.prog[p_idx] + self.relative_base ]

		else:
			print(f"Uh oh, invalid mval: {mval}")

		return (addr, val)

	def maybe_extend_memory(self, dest):

		# self.debug(f"Program memory length is {len(self.prog)}.")

		if dest>=len(self.prog):
			self.prog = self.prog + [0]*(dest-len(self.prog)+1)

		# self.debug(f"Program memory length is {len(self.prog)}.")

		return None

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
			self.debug(f"The operation is: {operation}")

			if operation==1: # add
				(addr1, val1) = self.get_param_addr_value(self.instr_ptr+1, modes[2])
				(addr2, val2) = self.get_param_addr_value(self.instr_ptr+2, modes[1])
				# dest = self.prog[self.instr_ptr+3]
				(dest, val3) = self.get_param_addr_value(self.instr_ptr+3, modes[0])
				self.debug(f"Add {val1} to {val2} and store at {dest}")
				self.maybe_extend_memory(dest)
				self.prog[dest] = val1 + val2
				self.instr_ptr += 4

			elif operation==2: # multiply
				(addr1, val1) = self.get_param_addr_value(self.instr_ptr+1, modes[2])
				(addr2, val2) = self.get_param_addr_value(self.instr_ptr+2, modes[1])
				# dest = self.prog[self.instr_ptr+3]
				(dest, val3) = self.get_param_addr_value(self.instr_ptr+3, modes[0])
				self.debug(f"Multiply {val1} to {val2} and store at {dest}")
				self.maybe_extend_memory(dest)
				self.prog[dest] = val1 * val2
				self.instr_ptr += 4

			elif operation==3:
				# save_input
				# dest = self.prog[self.instr_ptr+1]
				(dest, val) = self.get_param_addr_value(self.instr_ptr+1, modes[0])

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
				self.maybe_extend_memory(dest)
				self.prog[dest] = input_val
				self.instr_ptr += 2

			elif operation==4: # output
				(addr, output_val) = self.get_param_addr_value(self.instr_ptr+1, modes[0])
				self.debug(f"Output {output_val}.")
				self.outputs.append(output_val)
				self.instr_ptr += 2

			elif operation==5: # jump if true
				(addr1, val1) = self.get_param_addr_value(self.instr_ptr+1, modes[1])
				(addr2, val2) = self.get_param_addr_value(self.instr_ptr+2, modes[0])
				if val1 != 0:
					self.debug(f"Jump from {self.instr_ptr} to {val2}.")
					self.instr_ptr = val2
				else:
					self.debug(f"DO NOT jump from {self.instr_ptr} to {val2}.")
					self.instr_ptr += 3

			elif operation==6: # jump if false
				(addr1, val1) = self.get_param_addr_value(self.instr_ptr+1, modes[1])
				(addr2, val2) = self.get_param_addr_value(self.instr_ptr+2, modes[0])
				if val1 == 0:
					self.debug(f"Jump from {self.instr_ptr} to {val2}.")
					self.instr_ptr = val2
				else:
					self.debug(f"DO NOT jump from {self.instr_ptr} to {val2}.")
					self.instr_ptr += 3

			elif operation==7: # less than
				(addr1, val1) = self.get_param_addr_value(self.instr_ptr+1, modes[2])
				(addr2, val2) = self.get_param_addr_value(self.instr_ptr+2, modes[1])
				(dest, val3) = self.get_param_addr_value(self.instr_ptr+3, modes[0])
				self.maybe_extend_memory(dest)
				if val1 < val2:
					self.debug(f"Since {val1} < {val2}, store 1 at {dest}.")
					self.prog[dest] = 1
				else:
					self.debug(f"Since {val1} >= {val2}, store 0 at {dest}.")
					self.prog[dest] = 0
				self.instr_ptr += 4

			elif operation==8: # equals
				(addr1, val1) = self.get_param_addr_value(self.instr_ptr+1, modes[2])
				(addr2, val2) = self.get_param_addr_value(self.instr_ptr+2, modes[1])
				(dest, val3) = self.get_param_addr_value(self.instr_ptr+3, modes[0])
				self.maybe_extend_memory(dest)
				if val1 == val2:
					self.debug(f"Store 1 at {dest}.")
					self.prog[dest] = 1
				else:
					self.debug(f"Store 0 at {dest}.")
					self.prog[dest] = 0
				self.instr_ptr += 4

			elif operation==9: # change relative base
				(addr1, val1) = self.get_param_addr_value(self.instr_ptr+1, modes[0])
				self.debug(f"Adjusting relative base from {self.relative_base} to {self.relative_base+val1}.")
				self.relative_base += val1
				self.instr_ptr += 2

			else:
				self.debug(f"I am SQUAWK because the operation is: {operation}")
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

	elif operation in [5, 6]: #jump if
		while len(opstr)<4:
			opstr="0"+opstr

	elif operation in [3, 4, 9]: #store input, output; change relbase
		while len(opstr)<3:
			opstr="0"+opstr

	modes=[int(v) for v in list(opstr[:-2])]
	return(operation, modes)