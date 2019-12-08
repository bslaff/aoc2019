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

	image = np.asarray(layers)
	print(image.shape)
	result = np.zeros(shape=(layer_size,))

	image = image - 2 # now transparent is 0
	
	for n in range(num_layers):
		for k in range(layer_size):
			# print(image[:,k])
			nz_idx = np.nonzero(image[:,k])[0]
			result[k] = image[nz_idx[0],k] + 2

	# Now 0 black, 1 white, 2 transparent (gone)

	def getchar(x):
		if x==1:
			return "X"
		return " "

	result_x = np.asarray([getchar(x) for x in result])

	result_x = result_x.reshape((args.height, args.width))

	np.savetxt("./8b_out.txt", result_x, fmt='%s')

	return 0

if __name__=="__main__":

	run_main()