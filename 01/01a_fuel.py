import numpy as np
import argparse


def get_args():
	
	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file with one non-negative integer per line")
	
	return parser.parse_args()


def get_nums(args):

	f = open(args.infile, 'r')
	nums = f.readlines()
	f.close()

	nums = [n.strip() for n in nums]
	nums = [int(n) for n in nums]

	return(nums)


def run_main():

	args = get_args()
	nums = get_nums(args)

	nums = np.asarray(nums)
	result = np.sum( np.floor( nums / 3 ) - 2 )
	
	print("The result is: %i"%(result))
	return(result)


if __name__=='__main__':

	run_main()