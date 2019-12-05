import numpy as np
import argparse


def get_args():
	
	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")
	
	return parser.parse_args()


def get_prog(args):

	f = open(args.infile, 'r')
	prog = f.readlines()
	f.close()

	wire_1 = prog[0].strip().split(",")
	wire_2 = prog[1].strip().split(",")
	# ignore everything else

	return(wire_1, wire_2)


def wire_input_to_coordinates(wire):

	start = (0,0)
	result = [start]

	for mvt in wire:
		
		mvt = mvt.strip()

		dirx = mvt[0]
		num = int( mvt[1:] )

		if dirx=="R":
			coords = [(v, start[1]) for v in range(start[0]+1, start[0]+num+1)]
			start = (start[0]+num,start[1])

		elif dirx=="L":
			coords = [(v, start[1]) for v in range(start[0]-num, start[0])]
			start = (start[0]-num,start[1])

		elif dirx=="D":
			coords = [(start[0],v) for v in range(start[1]-num, start[1])]
			start = (start[0],start[1]-num)

		elif dirx=="U":
			coords = [(start[0],v) for v in range(start[1]+1, start[1]+num+1)]
			start = (start[0],start[1]+num)

		else:
			print("SQUAWK")

		result += coords

	return result


def run_main():

	args = get_args()
	(wire_1, wire_2) = get_prog(args)

	wire_1 = wire_input_to_coordinates(wire_1)
	wire_2 = wire_input_to_coordinates(wire_2)

	combined = sorted( list(set(wire_1)) + list(set(wire_2)) )

	intersections = set()

	for i in range(len(combined)-1):
		if combined[i] == combined[i+1]:
			intersections.add(combined[i])

	smallest_dist = float("inf")
	smallest_interx = None

	for interx in intersections:
		dist = abs(interx[0])+abs(interx[1])

		if dist==0:
			continue

		if dist < smallest_dist:
			smallest_dist = dist
			smallest_interx = interx

	print(f"Intersection {smallest_interx} has smallest distance of {smallest_dist} from origin.")

	return smallest_dist


if __name__=='__main__':

	run_main()
