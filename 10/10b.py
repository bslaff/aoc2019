import numpy as np
import argparse


def get_args():

	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")

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
			return np.asarray([0,1])
		return np.asarray([0,-1])

	if x>0:
		return np.asarray([1,0])
	return np.asarray([-1,0])


def get_theta(pair):

	x=pair[0]
	y=pair[1]

	hyp= (x**2 + y**2)**0.5 # hypotnuse length

	if x==0:
		if y>0:
			return 0
		elif y<0:
			return 180
		return 0 # hopefully never

	if x>0:
		return 90+(180-np.arccos(y/hyp))

	#x<0
	return 180+np.arccos(y/hyp)



def run_main():

	args = get_args()
	coords_arr = get_asteroid_coords(args)

	max_in_sight = -np.inf
	max_idx = None

	targ = np.asarray([COORDS, HERE])

	cent_coords = coords_arr - targ

	ratio_coords = np.apply_along_axis(get_ratios, 1, cent_coords).astype(int) # handles divide-by-zero case

	thetas = np.apply_along_axis(get_theta, 1, ratio_coords).astype(int)

	dsq = np.sum( np.power(cent_coords, 2), axis=1 ).astype(int)

	final = np.zeros( (coords_arr.shape[0], 6) )
	final[:, 0:2]=coords_arr
	final[:, 2:4]=ratio_coords
	final[:, 4]=thetas # should be 0 for (0,1) going clockwise up to 359...
	final[:, 5]=dsq

	final=final[final[:,4:6].argsort()].astype(int)
	# now columns 0-1 are original coords, 2-3 are reduced ratio coords, 4 is theta (clockwise from top), 5 is sq distance from target, sorted by THETA then DSQ

	final_order = []
	final_order.append()

	for j in range(1,final.shape[0]):


	d = dict()
	for j in range(final.shape[0]):
		x = tuple(final[j,2:4])
		if x not in s and x!=(0,0):
			d[x]=tuple(final[j,0:2])

	L = len(s)
	if L > max_in_sight:
		max_in_sight=L
		max_idx = i

	print(max_in_sight)
	print(coords_arr[max_idx,:])

	return 0


if __name__ == '__main__':

	run_main()