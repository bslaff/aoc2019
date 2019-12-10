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

	if pair[0]==0 and pair[1]==0:
		return np.asarray([0,0])

	if pair[0]!=0 and pair[1]!=0:
		return pair/np.gcd(pair[0], pair[1])

	elif pair[0]==0:
		if pair[1]>0:
			return np.asarray([0,1])
		return np.asarray([0,-1])

	if pair[0]>0:
		return np.asarray([1,0])
	return np.asarray([-1,0])



def run_main():

	args = get_args()
	coords_arr = get_asteroid_coords(args)

	max_in_sight = -np.inf
	max_idx = None

	for i in range(coords_arr.shape[0]):

		targ = coords_arr[i,:].copy()

		cent_coords = coords_arr - targ

		ratio_coords = np.apply_along_axis(get_ratios, 1, cent_coords).astype(int) # handles divide-by-zero case

		dsq = np.sum( np.power(cent_coords, 2), axis=1 ).astype(int)

		final = np.zeros( (coords_arr.shape[0], 5) )
		final[:, 0:2]=coords_arr
		final[:, 2:4]=ratio_coords
		final[:, 4]=dsq

		final=final[final[:,4].argsort()].astype(int)
		# now columns 0-1 are original coords, 2-3 are reduced ratio coords, 4 is sq distance from target, sorted by (4)

		s = set()
		for j in range(final.shape[0]):
			x = tuple(final[j,2:4])
			if x not in s and x!=(0,0):
				s.add(x)

		L = len(s)
		if L > max_in_sight:
			max_in_sight=L
			max_idx = i

	print(max_in_sight)
	print(coords_arr[max_idx,:])

	return 0


if __name__ == '__main__':

	run_main()