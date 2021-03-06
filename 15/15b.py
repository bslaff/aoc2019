import argparse
import numpy as np
from intcodeComputerNode import IntcodeComputerNode

START_CHAR='S'
UNEXPLORED_CHAR=' '
OXYGEN_CHAR='*'
ROBOT_CHAR='D'
EMPTY_CHAR='.'
WALL_CHAR='|'
OXYGEN_GAS_CHAR='G'

oxygen_x = -1
oxygen_y = -1

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

def hit_wall(board, robot):

	global WALL_CHAR

	if robot["dir"]=="NORTH":
		board[ robot['y']-1, robot['x'] ] = WALL_CHAR
	elif robot["dir"]=="WEST":
		board[ robot['y'], robot['x']-1 ] = WALL_CHAR
	elif robot["dir"]=="EAST":
		board[ robot['y'], robot['x']+1 ] = WALL_CHAR
	elif robot["dir"]=="SOUTH":
		board[ robot['y']+1, robot['x'] ] = WALL_CHAR

	return None


def take_one_step(board, robot):

	global ROBOT_CHAR
	global EMPTY_CHAR

	board[ robot['y'], robot['x'] ] = EMPTY_CHAR

	if robot["dir"]=="NORTH":
		robot['y'] -= 1
	elif robot["dir"]=="WEST":
		robot['x'] -= 1
	elif robot["dir"]=="EAST":
		robot['x'] += 1
	elif robot["dir"]=="SOUTH":
		robot['y'] += 1

	board[ robot['y'], robot['x'] ] = ROBOT_CHAR

	if not robot["is_backtracking"]:
		robot["path"].append( np.asarray([ robot['x'], robot['y'] ]) )

	return None

def at_oxygen(board, robot):

	global OXYGEN_CHAR

	board[ robot['y'], robot['x'] ] = OXYGEN_CHAR

	global oxygen_x
	global oxygen_y
	oxygen_x = robot['x']
	oxygen_y = robot['y']

	return None

def update_board(board, robot, outputs):

	for o in outputs:

		if o==0:
			hit_wall(board, robot)

		elif o==1:
			take_one_step(board, robot)

		elif o==2:
			take_one_step(board, robot)
			at_oxygen(board, robot)

		else:
			print("SQUAWK!!")

	return None

def disp_board(board):

	for i in range(board.shape[0]):
		print("".join(board[i,:]))

	return None

def get_process_user_input():

	valid = set([1, 2, 3, 4])
	v = -2
	first = True

	while v not in valid:
		if not first:
			print(f"Invalid input: {v}")
		first=False
		v = input('--> ')
		try:
			v = int(v.strip())
		except:
			continue

	return v

def update_robot_orientation(robot, user_instr):

	if user_instr==1:
		robot["dir"]="NORTH"
	elif user_instr==2:
		robot["dir"]="SOUTH"
	elif user_instr==3:
		robot["dir"]="WEST"
	elif user_instr==4:
		robot["dir"]="EAST"

	return None

def backtrack(robot):

	previous = robot["path"][-2]

	debug(previous)
	debug([robot['x'], robot['y']])
	
	diff_x = previous[0]-robot['x']
	diff_y = previous[1]-robot['y']

	debug(f"diff_y is {diff_y} which is {previous[1]}-{robot['y']}")

	L = len(robot["path"])
	robot["path"] = robot["path"][:(L-1)]

	if diff_x == 1: # Need to go east
		return 4
	if diff_x == -1: # Need to go west
		return 3
	if diff_y == 1: # Need to go south (down)
		return 2
	if diff_y == -1: # Need to go north (up)
		return 1

	debug("UH OH")
	return -1


def auto_get_input_explore_heuristic(board, robot, start):
	# Heuristic search:
	# Keep track of euclidean distance from start point
	# Keep track of explored nodes
	# Prioritize exploring nodes as a function of distance from origin. Closer==first
	# If tied, choose one at random
	# Return the robot's new ORIENTATION (1, 2, 3, 4)

	global UNEXPLORED_CHAR

	x = robot['x']
	y = robot['y']

	candidates = [ [x-1, y], [x+1, y], [x, y+1], [x, y-1] ]

	final_candidates = []
	for c in candidates:
		if board[ c[1], c[0] ] == UNEXPLORED_CHAR:
			final_candidates.append(c)

	if len(final_candidates) == 0:
		# Nothing new to see here! backtrack
		val = backtrack(robot)
		debug(f"Backtrack returned {val}")
		robot["is_backtracking"]=True
		return val

	robot["is_backtracking"]=False

	final_candidates = np.asarray(final_candidates)

	euc_distances = np.sum( np.power( final_candidates - start, 2), axis=1 )
	debug("EUC DISTANCES")
	debug(euc_distances)
	idx = np.argmin(euc_distances)

	if np.array_equal( final_candidates[idx], [x-1, y] ): # WEST
		return 3
	if np.array_equal( final_candidates[idx], [x+1, y] ): # EAST
		return 4
	if np.array_equal( final_candidates[idx], [x, y+1] ): # SOUTH
		return 2
	if np.array_equal( final_candidates[idx], [x, y-1] ): # NORTH
		return 1

	debug("SQUAWK!!!!")
	return -1

def get_neighbors(n, board):

	global WALL_CHAR

	x = n[0]
	y = n[1]

	candidates = [ (x, y+1), (x, y-1), (x+1, y), (x-1, y)]

	neighbors = []
	for c in candidates:
		if board[ c[1], c[0] ] != WALL_CHAR:
			neighbors.append(c)

	return neighbors


def run_main():

	global ROBOT_CHAR
	global UNEXPLORED_CHAR

	args = get_args()
	prog = get_prog(args)

	D = 50
	board = np.asarray( [[UNEXPLORED_CHAR]*D]*D )
	robot=dict()
	robot['x'] = int(D/2)
	robot['y'] = int(D/2)
	robot["path"] = [ np.asarray([ robot['x'], robot['y'] ]) ]

	start_x = robot['x']
	start_y = robot['y']
	start=np.asarray( [start_x, start_y] ).reshape( (1,2) ) # start position

	board[ robot['y'], robot['x'] ] = ROBOT_CHAR
	count=0

	debug(f"Board status move {count}:")
	disp_board(board)

	icn = IntcodeComputerNode("A", prog, [])

	debug(f"Getting user input:")
	# user_instr = get_process_user_input()
	user_instr = auto_get_input_explore_heuristic(board, robot, start)

	debug(f"Updating robot orientation")
	update_robot_orientation(robot, user_instr)

	debug(f"Updating intcodeComputerNode inputs with {user_instr}")
	icn.inputs.append(user_instr)
	L = len(icn.outputs)

	disp_board(board)
	debug(f"Beginning the loop!")

	while not icn.has_exited:
		count += 1
		debug(f"Count incremented to {count}")
		debug(f"Running intcodeComputerNode")
		icn.run_prog_from_current_state()
		debug(f"Ran intcodeComputerNode, updating board")
		update_board(board, robot, icn.outputs[L:])
		debug(f"Updated board.")
		L = len(icn.outputs)

		debug(f"Board status move {count}:")
		# disp_board(board)

		debug(f"Getting user input:")
		# user_instr = get_process_user_input()
		try:
			user_instr = auto_get_input_explore_heuristic(board, robot, start)
		except:
			# not the most elegent but whatever...
			break
		debug(f"Updating robot orientation")
		update_robot_orientation(robot, user_instr)
		debug(f"Updating intcodeComputerNode inputs with {user_instr}")
		icn.inputs.append(user_instr)

	# print(f"IntcodeComputerNode EXITED: {icn.has_exited}")

	board[start_y, start_x] = START_CHAR
	board[oxygen_y, oxygen_x] = OXYGEN_CHAR
	
	disp_board(board)
	print(f"Started at: {start_x}, {start_y}")
	print(f"Oxygen at: {oxygen_x}, {oxygen_y}")
	
	# Now: simulate the oxygen expansion with a sort of BFS
	target_count = 0
	target_set = set([START_CHAR, OXYGEN_CHAR, ROBOT_CHAR, EMPTY_CHAR])
	for char in board.flatten():
		if char in target_set:
			target_count += 1

	global OXYGEN_GAS_CHAR
	board[oxygen_y, oxygen_x] = OXYGEN_GAS_CHAR

	s = set([(oxygen_x,oxygen_y)])
	minutes = 0
	while True:
		new_s = set()
		for n in s:
			neighbors = get_neighbors(n, board)
			for neighbor in neighbors:
				x = neighbor[0]
				y = neighbor[1]
				if board[y,x] != OXYGEN_GAS_CHAR:
					board[y,x] = OXYGEN_GAS_CHAR
					new_s.add(neighbor)
		minutes+=1
		ox_count = np.sum( board.flatten() == OXYGEN_GAS_CHAR )
		print(f"ox_count is {ox_count}")
		if ox_count >= target_count:
			break
		s = new_s

	print(f"Done. ox_count is {ox_count} and target_count is {target_count}")
	print(f"The full spread took {minutes} minutes")

	return 0

def fully_oxygenated(board, target):

	global OXYGEN_GAS_CHAR

	return np.sum( board.flatten() == OXYGEN_GAS_CHAR ) == target

def debug(s):
	# print(s)
	return None

if __name__=="__main__":

	run_main()