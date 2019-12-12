import argparse
import numpy as np


def get_args():

	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")
	
	return parser.parse_args()


def get_arr(args):

	f = open(args.infile, 'r')
	lines = f.readlines()
	f.close()

	arr = np.zeros(shape=(len(lines), 6), dtype='int64')

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

		arr[i,:3] = np.asarray([x, y, z])

	return(arr)

def run_main():

	args = get_args()
	arr = get_arr(args)

	p_arr = np.array(arr[:, 0:3])
	v_arr = np.array(arr[:, 3:])

	initial_state_x = tuple(list(p_arr[:,0])+list(v_arr[:,0]))
	initial_state_y = tuple(list(p_arr[:,1])+list(v_arr[:,1]))
	initial_state_z = tuple(list(p_arr[:,2])+list(v_arr[:,2]))

	# Insight: determine the periods independently for each dimension, then take LCM.
	periods = np.asarray([-1]*3, dtype='int64') # int64 is key here!! lcm won't work otherwise

	c = 0
	while(True):

		for j in range(arr.shape[0]):

			diff = np.clip(p_arr - p_arr[j,:], a_min=-1, a_max=1)

			v_arr[j,:] += np.sum(diff, axis=0)

		c += 1

		p_arr += v_arr

		# state = tuple(list(p_arr.flatten())+list(v_arr.flatten()))
		state_x = tuple(list(p_arr[:,0])+list(v_arr[:,0]))
		state_y = tuple(list(p_arr[:,1])+list(v_arr[:,1]))
		state_z = tuple(list(p_arr[:,2])+list(v_arr[:,2]))

		if state_x == initial_state_x and periods[0] == -1:
			periods[0] = c
		if state_y == initial_state_y and periods[1] == -1:
			periods[1] = c
		if state_z == initial_state_z and periods[2] == -1:
			periods[2] = c

		if all(periods>0):
			print(f"Periods: {periods}")
			min_repeat = np.lcm.reduce(periods)
			print(f"REPEAT STATE after {min_repeat} iterations")
			break

		if c%10000==0:
			print(f"Tried {c} iterations. Periods so far: {periods}")

	return 0


if __name__=="__main__":

	run_main()