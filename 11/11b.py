import argparse
import numpy as np
from intcodeComputerNode import IntcodeComputerNode
from hullPaintingRobot import HullPaintingRobot


def get_args():

	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")
	# parser.add_argument("x", type=int, help="x start coord")
	# parser.add_argument("y", type=int, help="y start coord")
	
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

def getchar(x, robot):
	if x==robot.WHITE:
		return "#"
	return " "


def run_main():

	args = get_args()

	X_SIZE = 100
	Y_SIZE = 60
	X_COORD = int(X_SIZE/2)
	Y_COORD = int(Y_SIZE/2)
	base_grid_row = ['.']*X_SIZE
	base_grid = np.asarray( [base_grid_row for i in range(Y_SIZE)] )
	print(base_grid)

	prog = get_prog(args)
	icn = IntcodeComputerNode("A", prog, [])
	robot = HullPaintingRobot("JOE", X_COORD, Y_COORD, base_grid, icn)

	robot.paintGrid[Y_COORD,X_COORD]=robot.WHITE
	robot.paint()

	grid_out = np.asarray([getchar(x, robot) for x in robot.paintGrid.flatten()])
	grid_out = grid_out.reshape((Y_SIZE, X_SIZE))

	print(grid_out.shape)
	print(grid_out[:5,:5])

	np.savetxt("./out.txt", grid_out, fmt="%s")

	print(f"Painted at least once: {len(robot.paintedSet)}")

	return 0


if __name__=="__main__":

	run_main()