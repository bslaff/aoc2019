from intcodeComputerNode import IntcodeComputerNode

class HullPaintingRobot:

	def __init__(self, name, x, y, grid, icn):

		self.name = name
		self.x = x
		self.y = y
		self.paintGrid = grid.copy()
		self.intcodeComputerNode = icn

		self.paintedSet = set()
		self.direction="UP"
		self.BLACK="."
		self.WHITE="#"

	def paint(self):

		self.numOutputs = len(self.intcodeComputerNode.outputs)

		while not self.intcodeComputerNode.has_exited:

			self.get_input()
			
			self.intcodeComputerNode.run_prog_from_current_state()

			if self.should_paint_new_square():
				self.paint_square()
				self.turn_move()

	def get_input(self):

		val=self.paintGrid[self.y, self.x]
		if val==self.BLACK:
			self.intcodeComputerNode.inputs.append(0)
		else:
			self.intcodeComputerNode.inputs.append(1)
		return None

	def should_paint_new_square(self):

		# self.debug(f"My outputs have length {len(self.intcodeComputerNode.outputs)}: {self.intcodeComputerNode.outputs}")

		if self.numOutputs < len(self.intcodeComputerNode.outputs):

			self.numOutputs = len(self.intcodeComputerNode.outputs)
			return True 

		return False

	def paint_square(self):

		# self.maybe_extend_grid() # do later?

		paint_color = self.intcodeComputerNode.outputs[-2]
		if paint_color==0:
			self.debug(f"Painting {self.BLACK} at {self.x},{self.y}")
			self.paintGrid[self.y, self.x]=self.BLACK
		else:
			self.debug(f"Painting {self.WHITE} at {self.x},{self.y}")
			self.paintGrid[self.y, self.x]=self.WHITE

		pair = (self.x, self.y)
		if pair not in self.paintedSet:
			self.debug(f"Adding first-time paint to {pair} for a total of {len(self.paintedSet)} painted at least once.")
			self.paintedSet.add(pair)
		return None

	def turn_move(self):

		turn_dir = self.intcodeComputerNode.outputs[-1]

		self.debug(f"turn_dir is {turn_dir}")
		self.debug(f"Initially at {self.x},{self.y} facing {self.direction}.")

		if turn_dir==0: # left 90 degrees
			if self.direction=="UP":
				self.direction="LEFT"
				self.x -= 1
			elif self.direction=="LEFT":
				self.direction="DOWN"
				self.y += 1
			elif self.direction=="DOWN":
				self.direction="RIGHT"
				self.x += 1
			elif self.direction=="RIGHT":
				self.direction="UP"
				self.y -= 1

		elif turn_dir==1: # right 90 degrees
			if self.direction=="UP":
				self.direction="RIGHT"
				self.x += 1
			elif self.direction=="RIGHT":
				self.direction="DOWN"
				self.y += 1
			elif self.direction=="DOWN":
				self.direction="LEFT"
				self.x -= 1
			elif self.direction=="LEFT":
				self.direction="UP"
				self.y -= 1

		self.debug(f"Now at {self.x},{self.y} facing {self.direction}.")

	def debug(self, s):

		print(s)
		return None



