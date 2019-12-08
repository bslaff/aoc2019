import numpy as np
import argparse

def get_args():

	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")
	parser.add_argument("width", type=int, help="Image layer width")
	parser.add_argument("height", type=int, help="Image layer height")

	return parser.parse_args()

def run_main():

	args = get_args()

	f = open(args.infile, 'r')
	lines = f.readlines()
	f.close()

	lines = [line.strip() for line in lines]
	lines = [line for line in lines if len(line)>0]
	lines = "".join(lines)

	image = list(lines)
	image = [int(v) for v in image]

	print(len(image))
	# print(image[:10])

	layer_size = args.width*args.height

	# print(len(image)%layer_size)

	layers = []

	i=0
	num_layers = 0

	print(len(image))
	print(layer_size)

	while i+layer_size<=len(image):
		layers.append(image[i:(i+layer_size)])
		i += layer_size
		num_layers += 1

	print(len(layers)*len(layers[0]))

	count_d = dict()
	for n in list(range(num_layers)):
		count_d[n] = dict()
		
		for k in list(range(10)):
			count_d[n][k]=0

		for digit in layers[n]:
			count_d[n][digit] += 1

	# now get the result
	fewest_0 = np.inf
	fewest_0_layer = None
	for n in list(range(num_layers)):

		print(n, count_d[n][0], count_d[n][1]*count_d[n][2])

		if count_d[n][0] < fewest_0:
			fewest_0 = count_d[n][0]
			fewest_0_layer = n

	result = count_d[fewest_0_layer][1]*count_d[fewest_0_layer][2]

	print(f"The result is: {result} from layer {fewest_0_layer}")

	return 0

if __name__=="__main__":

	run_main()