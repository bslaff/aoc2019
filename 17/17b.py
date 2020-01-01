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


def disp_board(board):

	for i in range(board.shape[0]):
		print("".join(board[i,:]))

	return None

def disp_board_with_coords(board):

	print(board.dtype)

	p_board = np.empty( (board.shape[0]+1, board.shape[1]+1), dtype='<U1')
	p_board[1:,1:]=board.copy()
	p_board[0,:]=[0]+[v%10 for v in np.arange(p_board.shape[1]-1)]
	p_board[:,0]=[0]+[v%10 for v in np.arange(p_board.shape[0]-1)]

	for i in range(p_board.shape[0]):
		print("".join(p_board[i,:]))

	return None

def is_crossing(arr, y, x):

	conditions=[ 
	arr[y,x]!='.',
	arr[y-1,x]!='.',
	arr[y+1,x]!='.',
	arr[y,x-1]!='.',
	arr[y,x+1]!='.'
	]

	return all(conditions)

def run_main():

	args = get_args()
	prog = get_prog(args)

	### Path based on all that other mess below (see run_main_dev()):

	# main: A,B,A,C,A,B,C,C,A,B
	# A: R,8,L,10,R,8
	# B: R,12,R,8,L,12
	# C: L,12,L,10,L,8

	main_routine = list("A,B,A,C,A,B,C,C,A,B\n")
	A = list("R,8,L,10,R,8\n")
	B = list("R,12,R,8,L,8,L,12\n")
	C = list("L,12,L,10,L,8\n")
	video = list("y\n")

	# print(f"main_routine: {main_routine}")
	# print(f"A: {A}")
	# print(f"B: {B}")
	# print(f"C: {C}")
	# print(f"video: {video}")

	main_routine = [ord(x) for x in main_routine]
	A = [ord(x) for x in A]
	B = [ord(x) for x in B]
	C = [ord(x) for x in C]
	video=[ord(x) for x in video]

	# print(f"main_routine: {main_routine}")
	# print(f"A: {A}")
	# print(f"B: {B}")
	# print(f"C: {C}")
	# print(f"video: {video}")

	prog[0] = 2
	icn = IntcodeComputerNode("ENIAC", prog, [])
	out_ptr=0

	print("Running program:")
	icn.run_prog_from_current_state()
	# print(f"icn exited: {icn.has_exited}")

	print( ''.join([chr(v) for v in icn.outputs[out_ptr:]]) )
	out_ptr=len(icn.outputs)

	# s = ''.join([chr(v) for v in icn.outputs])
	# arr = [v for v in s.split('\n') if len(v.strip())>0]

	# arr = np.asarray([list(s) for s in arr])
	# disp_board(arr)

	print(f"Adding main to input: {main_routine}")
	for v in main_routine:
		icn.inputs.append(v)

	print("Running program:")
	icn.run_prog_from_current_state()
	print( ''.join([chr(v) for v in icn.outputs[out_ptr:]]) )
	out_ptr=len(icn.outputs)

	print(f"Adding A to input: {A}")
	for v in A:
		icn.inputs.append(v)

	print("Running program:")
	icn.run_prog_from_current_state()
	print( ''.join([chr(v) for v in icn.outputs[out_ptr:]]) )
	out_ptr=len(icn.outputs)

	print(f"Adding B to input: {B}")
	for v in B:
		icn.inputs.append(v)

	print("Running program:")
	icn.run_prog_from_current_state()
	print( ''.join([chr(v) for v in icn.outputs[out_ptr:]]) )
	out_ptr=len(icn.outputs)

	print(f"Adding C to input: {C}")
	for v in C:
		icn.inputs.append(v)

	print("Running program:")
	icn.run_prog_from_current_state()
	print( ''.join([chr(v) for v in icn.outputs[out_ptr:]]) )
	out_ptr=len(icn.outputs)

	print(f"Adding video to input: {video}")
	for v in video:
		icn.inputs.append(v)

	print("Running program:")
	icn.run_prog_from_current_state()
	print( ''.join([chr(v) for v in icn.outputs[out_ptr:]]) )
	out_ptr=len(icn.outputs)

	print(f"Final output: {icn.outputs[-1]}")

	return 0


def run_main_dev():

	args = get_args()
	prog = get_prog(args)

	icn = IntcodeComputerNode("A", prog, [])
	icn.run_prog_from_current_state()
	debug( ''.join([chr(v) for v in icn.outputs]) )

	s = ''.join([chr(v) for v in icn.outputs])
	arr = [v for v in s.split('\n') if len(v.strip())>0]

	arr = np.asarray([list(s) for s in arr])
	disp_board(arr)
	debug(arr.shape)

	XX = range(1,(arr.shape[1]-1))
	YY = range(1,(arr.shape[0]-1))

	intersections = []

	for y in YY:
		for x in XX:
			if is_crossing(arr, y, x):
				intersections.append((x, y))

	total=0
	params=[v[0]*v[1] for v in intersections]
	total=sum(params)

	# print(f"intersections: {intersections}")
	# print(f"{len(intersections)} intersections")
	# print(f"parameters: {params}")
	# print(f"{len(params)} parameters")
	# print(f"The total is {total}")

	### Convert the map to a graph.
	### Nodes: are the WALKWAYS. Each walkway between a {dead end, intersection} and a {dead end, intersection} is a graph node
	### Undirected edges of weight 1 connect walkways if they are adjacent
	### Each node (walkway) includes a PATH 1 and PATH 2. PATH 1 might be U,8,R,8 and PATH 2 would be the reverse: L,8,D,8

	### You know, we could solve it that way
	### But this map is small enough that we can possibly figure this out manually
	### Seriously let's try that first. Sometimes the dumbest way is best...

	### Ok eyeballing this:
	# R,8,L,10,R,8,R,2,R,6,R,0,R,12,R,8,R,6,R,8 [done top left and first box]
	# R,0,R,10,R,2,R,2,R,2,R,2,R,2,L,8,R,6,R,8,R,6,R,8 # done mid left small and big box, now starting horizontal box mid left
	# L,6,R,2,R,6,R,2,R,6,R,2 # done the horizontal box mid left
	# L,2,L,10,R,2,R,6,L,10,R,8,L,8,R,10,R,12,R,8,L,10,R,6,R,2,L,10,R,2 # done big bottom right loop, now at the top of it
	# L,2,R,6,R,2,R,6,R,2,R,6 # done small horizontal box just above the big bottom right loop
	# L,6,R,10 # done top right isolated path
	# R,12,R,8,R,10,R,10,R,14,R,8,R,8,L,6 # done everything top right, done everything period.

	### Ok, based on above a prospective path is (with corrections made based on tests)
	# R='R'
	# L='L'
	# pp=[R,8,L,10,R,8,R,2,R,6,R,0,R,12,R,8,R,6,R,8]
	# pp += [R,0,R,10,R,2,R,2,R,2,R,2,R,2,L,8,R,6,R,8,R,6,R,8]
	# pp += [L,6,R,2,R,6,R,2,R,6,R,2]
	# pp += [L,2,L,10,R,2,R,6,L,10,R,8,L,8,R,10,R,12,R,8,L,10,R,6,R,2,L,10,R,2]
	# pp += [L,2,R,6,R,2,R,6,R,2,R,6]
	# pp += [L,6,R,10]
	# pp += [R,12,R,8,R,10,R,12,R,12,R,8,R,8,L,6]

	### Ok, after playing with that, new approach based on heuristic: don't turn until we have to (hence, limit total path command length):
	# R,8,L,10,R,8,R,12,R,8,L,8,L,12,R,8,L,10,R,8,L,12,L,10,L,8,R,8,L,10,R,8,R,12,R,8,L,8,L,12,L,12,L,10,L,8,L,12,L,10,L,8,R,8,L,10,R,8,R,12,R,8,L,8,L,12
	# That's a complete traversal ending at the other dead end. We'll run with it:

	### Ok based on above a prospective path is (with corrections made based on tests)
	R='R'
	L='L'
	pp=[R,8,L,10,R,8,R,12,R,8,L,8,L,12,R,8,L,10,R,8,L,12,L,10,L,8,R,8,L,10,R,8,R,12,R,8,L,8,L,12,L,12,L,10,L,8,L,12,L,10,L,8,R,8,L,10,R,8,R,12,R,8,L,8,L,12]

	### First thing to do is confirm that this is actually a correct path

	# L = len(pp)
	# i=0
	# direction='N'
	# x=0
	# y=10
	# while i<L:
	# 	direction=get_direction(pp[i],direction)
	# 	(x,y) = update_map(arr, direction, pp[i+1], x, y)
	# 	disp_board_with_coords(arr)
	# 	print(pp[i:(i+2)])
	# 	i+=2

	# 	iii = input() # don't use it
	# 	if iii.strip()=='q':
	# 		exit()

	## Above path is right! Well, it's one correct path.
	## Now we just need to see if it's convertable to a movement program for the robot. If not, we need a new path.

	pp_str = ",".join([str(v) for v in pp])+"," # take last comma away later, useful for now
	print(pp_str)
	print(len(pp_str))

	### Let's get a map of repeated substrings up to length 20, since that's the longest a movement function can be

	### Ok good but there is a lot of redundancy in there. Remove the cycle-duplicates.
	### Actually wait, that may matter. Don't remove them yet.

	### Ok good. Now we need to choose three movement functions
	### It looks like this entire thing needs to compose into these movement functions. So, yikes.
	### If that doesn't work for our current path, then we need a new path for which that's possible.
	### Some hard constraints on the path, though. Has to start a certain way for the top left loop, and has to accomodate the big bottom right loop.

	print(f"main {len(pp_str)}: {pp_str}")
	print()

	# A=find_best_repeat(pp_str)
	A='R,8,L,10,R,8,' # Refinement based on first attempt
	pp_str=pp_str.replace(A, 'A,').replace(',,',',')
	print(f"A {len(A)}: {A}")
	print(f"After A substitution: {pp_str}")
	print()

	B=find_best_repeat(pp_str)
	pp_str=pp_str.replace(B, 'B,').replace(',,',',')
	print(f"B {len(B)}: {B}")
	print(f"After B substitution: {pp_str}")
	print()

	C=find_best_repeat(pp_str)
	pp_str=pp_str.replace(C, 'C,').replace(',,',',')
	print(f"C {len(C)}: {C}")
	print(f"After C substitution: {pp_str}")
	print()
	print()

	print(f"main {len(pp_str)}: {pp_str}")
	print(f"A {len(A)}: {A}")
	print(f"B {len(B)}: {B}")
	print(f"C {len(C)}: {C}")

	## Wowzers, that did it:
	# main: A,B,A,C,A,B,C,C,A,B
	# A: R,8,L,10,R,8
	# B: R,12,R,8,L,8,L,12
	# C: L,12,L,10,L,8

	##### WHAT FOLLOWS WAS NOT PART OF THE ULTIMATE SOLUTION. It was a failed extension of the first try above (before the second try, which worked).
	### Ok what this has shown me is that we need a more economical path
	### Probably needs to END at that only dead end so we don't turn around
	### How many possible rules are there?
	### Commands: 2, 3, 4 (one command: "R" "L" then number). 3 options.
	### How many numbers? 2, 4, 6, 8, 10, 12, 14 that's it. 7 options. With rapid elimination.
	### So that's 2*7 choices per command, 14^4 is not that bad plus we can eliminate.
	### Alright, brute force it? That may not be enough though. May have more than one solution.
	### But can't have that many. Well, keep all solutions then pick the valid ones (less than 20 chars etc)

	# p_cmds = []
	# for chgdir in ['R','L']:
	# 	for nsteps in [2, 4, 6, 8, 10, 12, 14]:
	# 		p_cmds.append([chgdir, nsteps])

	# p_routines = []
	# for i in range(len(p_cmds)):
	# 	for j in range(len(p_cmds)):
	# 		p_routines.append(p_cmds[i]+p_cmds[j])

	# for i in range(len(p_cmds)):
	# 	for j in range(len(p_cmds)):
	# 		for k in range(len(p_cmds)):
	# 			p_routines.append(p_cmds[i]+p_cmds[j]+p_cmds[k])

	# for i in range(len(p_cmds)):
	# 	for j in range(len(p_cmds)):
	# 		for k in range(len(p_cmds)):
	# 			for l in range(len(p_cmds)):
	# 				p_routines.append(p_cmds[i]+p_cmds[j]+p_cmds[k]+p_cmds[l])

	# for i in range(len(p_cmds)):
	# 	for j in range(len(p_cmds)):
	# 		for k in range(len(p_cmds)):
	# 			for l in range(len(p_cmds)):
	# 				for m in range(len(p_cmds)):
	# 					p_routines.append(p_cmds[i]+p_cmds[j]+p_cmds[k]+p_cmds[l]+p_cmds[m])

	# print(len(p_routines))

	### 26390 possible routines. Cool, but we still don't want to test that^4 possibilities.
	### Start by seeing what the first routine COULD be. Not many options.
	### Based on that see what the second routine COULD be. Etc.
	### Should eliminate pretty fast that way.

	# on_scaffold=set(['#','^','>','<'])
	# p_first = []

	# for j in range(len(p_routines)):

	# 	pp = p_routines[j]
	# 	# pp = ['R',8,'L',10,'R',8]

	# 	L = len(pp)
	# 	i=0
	# 	direction='N'
	# 	x=0
	# 	y=10
	# 	full_traversal=[]

	# 	while i<L:
	# 		direction=get_direction(pp[i],direction)
	# 		((x,y), traversed) = update_position(direction, pp[i+1], x, y)
	# 		full_traversal += traversed # might not have the right order but ok
	# 		i+=2

	# 	if all_scaffold(arr, full_traversal):
	# 		if ends_at_non_midpoint(arr,x,y):
	# 			p_first.append(pp)

	# 	# break

	# print(p_first)
	# print(len(p_first))

	return 0

def ends_at_non_midpoint(arr, x, y):

	# Rule: you can't have empty space on only two opposite sides
	# Everything else is ok

	N=arr[y-1,x]
	S=arr[y+1,x]
	E=arr[y,x+1]
	W=arr[y,x-1]

	if N=='.' and S=='.':
		if E!='.' and W!='.':
			return False

	if E=='.' and W=='.':
		if N!='.' and S!='.':
			return False

	return True

def all_scaffold(arr, positions):

	for p in positions:
		x = p[0]
		y = p[1]
		if arr[y,x]=='.':
			return False

	return True

def find_best_repeat(pp_str):

	repeats=dict()
	for L in range(8,21): # 20 char including comma is allowed
		for i in range(len(pp_str)-L):
			test_str = pp_str[i:(i+L)]
			if not test_str[-1]==',': # invalid
				continue
			if not test_str[0] in ['R','L']:
				continue

			test_str_l=test_str.split(',')
			if test_str_l[-1] in ['R', 'L'] or test_str_l[-2] in ['R', 'L']:
				continue

			if 'A' in test_str or 'B' in test_str or 'C' in test_str:
				continue
			if test_str in repeats.keys():
				continue
			c = pp_str.count(test_str)
			if c>1:
				repeats[test_str]=c

	# print(repeats)
	# print(len(repeats.keys()))

	scored=[]
	for k in repeats.keys():
		scored.append( (k, repeats[k]*len(k)) )

	scored=sorted(scored, key=lambda x: x[1], reverse=True)

	print(f"Best candidates: {scored[:10]}")

	best=scored[0][0]
	print(f"Best: {scored[0]}")
	return best

def update_position(direction, nsteps, x, y):

	if direction=='N':
		traversed=[(x,y-i) for i in range(nsteps+1)]
		return ((x,y-nsteps), traversed)

	if direction=='S':
		traversed=[(x,y+i) for i in range(nsteps+1)]
		return ((x,y+nsteps), traversed)

	if direction=='E':
		traversed=[(x+i,y) for i in range(nsteps+1)]
		return ((x+nsteps,y), traversed)

	if direction=='W':
		traversed=[(x-i,y) for i in range(nsteps+1)]
		return ((x-nsteps,y),traversed)


def update_map(arr, direction, nsteps, x, y):

	if direction=='N':
		arr[(y-nsteps):y,x]='$'
		return (x,y-nsteps)

	if direction=='S':
		arr[(y+1):(y+nsteps+1),x]='$'
		return (x,y+nsteps)

	if direction=='E':
		arr[y,(x+1):(x+nsteps+1)]='$'
		return (x+nsteps,y)

	if direction=='W':
		arr[y,(x-nsteps):x]='$'
		return (x-nsteps,y)



def get_direction(turn_command, current_direction):

	if current_direction=='N':
		if turn_command=='R':
			return 'E'
		return 'W'

	if current_direction=='E':
		if turn_command=='R':
			return 'S'
		return 'N'

	if current_direction=='S':
		if turn_command=='R':
			return 'W'
		return 'E'

	if current_direction=='W':
		if turn_command=='R':
			return 'N'
		return 'S'

def debug(s):
	print(s)
	return None

if __name__=="__main__":

	run_main()
	# run_main_dev()