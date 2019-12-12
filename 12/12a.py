import argparse
import numpy as np


def get_args():

	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")
	parser.add_argument("n", type=int, help="Number of time steps")
	
	return parser.parse_args()


def get_arr(args):

	f = open(args.infile, 'r')
	lines = f.readlines()
	f.close()

	arr = np.zeros(shape=(len(lines), 6)).astype(int)

	for i in range(len(lines)):

		line = lines[i]

		# print(line)

		a = line.find('=')
		b = line.find(',')
		x = int(line[(a+1):b])
		line=line[(b+1):]

		a = line.find('=')
		b = line.find(',')
		y = int(line[(a+1):b])
		line=line[(b+1):]

		a = line.find('=')
		b = line.find('>')
		z = int(line[(a+1):b])
		line=line[(b+1):]

		arr[i,:3] = np.asarray([x, y, z]).astype(int)

	return(arr)

def run_main():

	args = get_args()
	arr = get_arr(args)

	for i in range(args.n):

		for j in range(arr.shape[0]):

			diff = arr - arr[j,:]

			arr[j,3] += ( np.sum( diff[:,0] > 0 ) - np.sum( diff[:,0] < 0 ) )
			arr[j,4] += ( np.sum( diff[:,1] > 0 ) - np.sum( diff[:,1] < 0 ) )
			arr[j,5] += ( np.sum( diff[:,2] > 0 ) - np.sum( diff[:,2] < 0 ) )

		arr[:, 0:3] += arr[:, 3:]

	p_en = np.sum( np.abs( arr[:, 0:3] ), axis=1 )
	k_en = np.sum( np.abs( arr[:, 3:] ), axis=1 )

	total_en = np.sum( np.multiply(p_en, k_en) )

	print(f"Total energy: {total_en}")

	return 0


if __name__=="__main__":

	run_main()