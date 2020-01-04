import argparse
import numpy as np
import math

def get_args():

	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")
	
	return parser.parse_args()

def get_nums(args):

	f = open(args.infile, 'r')
	lines = f.readlines()
	f.close()

	lines = "".join([line.strip() for line in lines if len(line.strip())>0])
	nums = np.asarray([int(v) for v in lines])

	return nums

def fft(nums, n_phases, pattern):

	if n_phases == 0:
		return nums

	L = nums.shape[0]
	P = pattern.shape[0]

	X = np.zeros(shape=(L,L))
	for i in range(L):
		ntimes_each = i+1
		num_distinct_elts = int(math.ceil(L/ntimes_each)+1)
		# debug(f"ntimes_each {ntimes_each}, num_distinct_elts {num_distinct_elts}")
		pattern_i = np.repeat(pattern[:num_distinct_elts], ntimes_each)
		X[i,:] = pattern_i[1:(L+1)]

	prods = X @ nums
	new_nums = np.abs(prods) % 10 # get ones digits

	# print(f"n_phases {n_phases}")
	# print(X)
	# print(nums)
	# print(prods)
	# print(new_nums)
	# print()

	# exit()

	return fft(new_nums, n_phases-1, pattern)

def run_main():

	args = get_args()
	nums = get_nums(args)

	n_phases=100
	pattern=[0,1,0,-1]

	# augment pattern to length nums
	pattern = pattern * int(math.ceil(nums.shape[0]/len(pattern))+1)
	pattern = np.asarray(pattern[:(nums.shape[0]+1)])

	output = fft(nums.reshape((nums.shape[0], 1)), n_phases, pattern)
	# print(output.flatten())
	final_output = "".join([str(int(v)) for v in output.flatten()])
	print(f"final output: {final_output}")
	print(f"first eight digits: {final_output[:8]}")

	return 0

def debug(s):
	print(s)
	return None

if __name__=="__main__":

	run_main()