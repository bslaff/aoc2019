import numpy as np
import argparse


def get_args():
	
	parser = argparse.ArgumentParser()
	parser.add_argument("start", type=int, help="Lower bound")
	parser.add_argument("finish", type=int, help="Upper bound")
	
	return parser.parse_args()


def is_nondecr(val):

	i = 0
	while i<5:
		if val[i]>val[i+1]:
			return False
		i += 1

	return True

def has_two_adj_same(val):

	i = 0
	while i<5:
		if val[i]==val[i+1]:
			return True
		i += 1

	return False

def increment_place(val, place):

	if val[5-place]==9:
		val[5-place] = 0
		increment_place(val, place+1)
	else:
		val[5-place] += 1

	return True


def increment(val):
	increment_place(val, 0)


def getvalue(val):
	return sum([val[i]*(10**(5-i)) for i in range(6)])


def run_main():

	args = get_args()

	val = [int(v) for v in list(str(args.start))]

	c=0
	while getvalue(val)<=args.finish:
		if is_nondecr(val) and has_two_adj_same(val):
			c+=1
		increment(val)

	print(c)
	return(c)


if __name__=='__main__':

	run_main()
