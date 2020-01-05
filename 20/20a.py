import argparse
import numpy as np
from copy import copy, deepcopy
import itertools

def get_args():

	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")
	
	return parser.parse_args()

def maybe_add_key_endpoint(portals_d, k, x, y):

	if k not in portals_d.keys():
		# print(f"Adding {k} key 1: {x}, {y}")
		portals_d[k]=dict()
		portals_d[k]['1']=dict()
		portals_d[k]['1']['x']=x
		portals_d[k]['1']['y']=y
	else:
		if '2' not in portals_d[k].keys():
			# print(f"Adding {k} key 2: {x}, {y}")
			portals_d[k]['2']=dict()
			portals_d[k]['2']['x']=x
			portals_d[k]['2']['y']=y
		else:
			pass # already found the two endpoints

	return None


def maybe_add_portal(arr, x, y, upper_set, portals_d):

	# print(f"Checking {x}, {y}")
	if x-2>=0:
		if ord(arr[y,x-1]) in upper_set and arr[y,x-2]=='.':
			k = arr[y,x-1]+arr[y,x]
			maybe_add_key_endpoint(portals_d, k, x-2, y)
	if x+2<arr.shape[1]:
		if ord(arr[y,x+1]) in upper_set and arr[y,x+2]=='.':
			k = arr[y,x]+arr[y,x+1]
			maybe_add_key_endpoint(portals_d, k, x+2, y)
	if y-2>=0:
		if ord(arr[y-1,x]) in upper_set and arr[y-2,x]=='.':
			k = arr[y-1,x]+arr[y,x]
			maybe_add_key_endpoint(portals_d, k, x, y-2)
	if y+2<arr.shape[0]:
		if ord(arr[y+1,x]) in upper_set and arr[y+2,x]=='.':
			k = arr[y,x]+arr[y+1,x]
			maybe_add_key_endpoint(portals_d, k, x, y+2)

	return None


def run_main():

	args = get_args()

	f = open(args.infile, 'r')
	lines = f.readlines()
	f.close()

	lines = [list(line.strip('\n')) for line in lines if len(line)>0]
	arr = np.asarray(lines)

	# first figure out where the portals are, and lead to
	# then, dijkstra to find shortest path

	portals_d = dict()

	upper_set = set(range(65, 91))

	for y in range(arr.shape[0]):
		for x in range(arr.shape[1]):
			o = ord(arr[y,x])
			# print(f"Checking {o} from arr[{y},{x}]")
			if o in upper_set:
				maybe_add_portal(arr, x, y, upper_set, portals_d)

	link_d = dict()

	# print(portals_d.keys())

	for portal in portals_d.keys():

		if portal in ['AA','ZZ']:
			continue

		x1=portals_d[portal]['1']['x']
		y1=portals_d[portal]['1']['y']
		x2=portals_d[portal]['2']['x']
		y2=portals_d[portal]['2']['y']

		link_d[(x1,y1)]=(x2,y2)
		link_d[(x2,y2)]=(x1,y1)

	start_x = portals_d['AA']['1']['x']
	start_y = portals_d['AA']['1']['y']

	target_x = portals_d['ZZ']['1']['x']
	target_y = portals_d['ZZ']['1']['y']

	# print(f"Working with links: {link_d}")

	arr_minDist = dijkstra(arr, start_x, start_y, link_d)

	target_dist = int( arr_minDist[target_y, target_x] )

	print(f"Min distance from start to finish is: {target_dist}")

	return 0	

# make sure to send a COPY of keys_d in here if we don't want the main version modified
def dijkstra(arr, x_start, y_start, link_d):
	# Keep track of dependencies:
	# Keep track of each door we pass as we go along. Store in node.
	# In the min step of dijkstra, if we replace the min dist for a node, also replace the dependency list.
	# That way each node has a record of the keys needed to get there from the middle.

	arr_visited = np.zeros(shape=arr.shape)
	arr_visited[y_start,x_start] = 1

	arr_minDist = np.ones(shape=arr.shape) * np.inf
	arr_minDist[y_start,x_start] = 0

	open_set = {(x_start, y_start)}

	while len(open_set)>0:

		# choose node with least distance so far
		least_dist = np.inf
		least_x = None
		least_y = None

		for pos in open_set:
			x = pos[0]
			y = pos[1]

			if arr_minDist[y,x] < least_dist:

				least_dist = arr_minDist[y,x]
				least_x = x
				least_y = y

		x = least_x
		y = least_y

		dist_here = arr_minDist[y,x]
		dist_nbhrs_tmp = dist_here + 1

		neighbors = get_neighbors(arr, x, y, link_d)

		for n in neighbors:
			xx = n[0]
			yy = n[1]
			is_warp = n[2]

			warp_penalty = 0
			if is_warp:
				warp_penalty = 1

			if dist_nbhrs_tmp + warp_penalty < arr_minDist[yy,xx]:

				arr_minDist[yy,xx] = dist_nbhrs_tmp + warp_penalty

		unvisited_nhbrs = get_unvisited_neighbors(neighbors, arr_visited, arr_minDist) # return in ascending order of distance, so we can iterate

		# print(f"Evaluating {x}, {y} with unvisited neighbors {unvisited_nhbrs}")

		open_set.remove((x, y))
		arr_visited[y,x]=1

		for nhbr in unvisited_nhbrs:

			open_set.add( nhbr )
 
	return arr_minDist

# def dijkstra_rec(arr, x, y, arr_visited, arr_minDist, link_d):

# 	dist_here = arr_minDist[y,x]
# 	dist_nbhrs_tmp = dist_here + 1

# 	neighbors = get_neighbors(arr, x, y, link_d)

# 	for n in neighbors:
# 		xx = n[0]
# 		yy = n[1]

# 		if dist_nbhrs_tmp < arr_minDist[yy,xx]:

# 			arr_minDist[yy,xx] = dist_nbhrs_tmp

# 	arr_visited[y,x]=1

# 	unvisited_nhbrs = get_unvisited_neighbors(neighbors, arr_visited, arr_minDist) # return in ascending order of distance, so we can iterate

# 	print(f"Evaluating {x}, {y} with unvisited neighbors {unvisited_nhbrs}")

# 	for next_nhbr in unvisited_nhbrs:

# 		next_x = next_nhbr[0][0]
# 		next_y = next_nhbr[0][1]

# 		dijkstra_rec(arr, next_x, next_y, arr_visited, arr_minDist, link_d) # arr_minDist will be modified sequentially

# 	return True

def get_neighbors(arr, x, y, link_d):

	prospects = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]

	neighbors = []

	for p in prospects:
		xx = p[0]
		yy = p[1]

		if xx<0 or xx>=arr.shape[1]:
			continue

		if yy<0 or yy>=arr.shape[0]:
			continue

		is_warp = False
		if (xx, yy) in link_d.keys():

			is_warp = True
			key = (xx, yy)

			xx = link_d[key][0]
			yy = link_d[key][1]

		c = arr[yy,xx]

		if c=='.':
			neighbors.append((xx,yy,is_warp))

	return neighbors

def get_unvisited_neighbors(neighbors, arr_visited, arr_minDist):

	uv = []

	for n in neighbors:

		x = n[0]
		y = n[1]

		if arr_visited[y,x]==1:
			continue # visted

		uv.append( (x,y) )

	return uv

def print_map(arr):

	for i in range(arr.shape[0]):
		print("".join(arr[i,:]))

	return 0

def debug(s):
	print(s)
	return None

if __name__=="__main__":

	run_main()