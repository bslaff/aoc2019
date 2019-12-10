import numpy as np
import argparse


def get_args():

	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")
	parser.add_argument("x", type=int, help="x coord of center")
	parser.add_argument("y", type=int, help="y coord of center")
	parser.add_argument("n", type=int, help="nth asteroid to be destroyed")
	
	return parser.parse_args()

def get_asteroid_coords(args):

	f = open(args.infile, 'r')
	lines = f.readlines()
	f.close()

	lines = [line.strip() for line in lines]

	height = len(lines)
	width = len(lines[0])

	coords = []

	for y in range(height):
		for x in range(width):
			if lines[y][x]=="#":
				coords.append((x,y))

	coords = sorted(coords)

	coords_arr = np.zeros(shape=(len(coords), 2))
	for i in range(len(coords)):
		coords_arr[i,:] = coords[i]

	return coords_arr.astype(int)

def get_ratios(pair):

	x=pair[0]
	y=pair[1]

	if x==0 and y==0:
		return np.asarray([0,0])

	if x!=0 and y!=0:
		return pair/np.gcd(x, y)

	elif x==0:
		if y>0:
			return np.asarray([0,-1])
		return np.asarray([0,1])

	if x>0:
		return np.asarray([1,0])
	return np.asarray([-1,0])


def get_theta(pair):

	x= pair[0]
	y= -pair[1] # in coordinates, y going down increases. in my theta space, y going up increases.

	hyp= (x**2 + y**2)**0.5 # hypotnuse length

	if x==0:
		if y>0:
			return 0
		elif y<0:
			return 180
		return 0 # hopefully never

	if x>0:
		return 90-np.degrees(np.arcsin(y/hyp))

	#x<0
	return 270+np.degrees( np.arcsin(y/hyp) )



def run_main():

	args = get_args()
	coords_arr = get_asteroid_coords(args)

	max_in_sight = -np.inf
	max_idx = None

	# targ = np.asarray([29, 28])
	# targ = np.asarray([11, 13])
	targ = np.asarray([args.x, args.y])

	cent_coords = coords_arr - targ

	ratio_coords = np.apply_along_axis(get_ratios, 1, cent_coords).astype(int) # handles divide-by-zero case

	thetas = np.apply_along_axis(get_theta, 1, ratio_coords).astype(float)

	dsq = np.sum( np.power(cent_coords, 2), axis=1 ).astype(int)

	final = np.zeros( (coords_arr.shape[0], 7) ).astype(float)
	final[:, 0:2]=coords_arr
	final[:, 2:4]=ratio_coords
	final[:, 4]=thetas # should be 0 for (0,1) going clockwise up to 359...
	final[:, 5]=dsq
	final[:,6]=[-1]*final.shape[0] # will contain final order

	final=final[ final[:,5] != 0 ] # remove the base asteroid, we don't shoot our own asteroid

	final=final[final[:,4].argsort()]
	# now columns 0-1 are original coords, 2-3 are reduced ratio coords, 4 is theta (clockwise from top), 5 is sq distance from target, sorted by THETA
	# now will pass through and set destroy order for one ast at a time per theta, in order of increasing theta (theta=0 should be 12 oclock, not 3 oclock)

	order_idx = 1 # count from ONE not ZERO so that 200th is right
	last_added_theta = -1

	while np.min( final[:,6] ) < 1:

		for j in range(final.shape[0]):

			this_order = final[j,6]
			this_theta = final[j,4]

			if this_order >= 1:
				continue

			if last_added_theta == this_theta:
				continue
			else:
				final[j,6] = order_idx
				order_idx += 1
				last_added_theta = this_theta

		last_added_theta = -1 # reset for each new circle

	final=final[final[:,6].argsort()]

	final_x = final[args.n-1,0]
	final_y = final[args.n-1,1]
	print(f"Key: {int(100*final_x+final_y)}")

	return 0

def debug(s):

	print(s)
	return None

if __name__ == '__main__':

	run_main()