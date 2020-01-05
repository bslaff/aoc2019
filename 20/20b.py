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

	arr_minDist, path = dijkstra(arr, start_x, start_y, link_d, target_x, target_y)

	target_dist = int( arr_minDist[target_y, target_x, 0] )

	print(f"Optimal path is: {path}")

	print(f"Min distance from start to finish is: {target_dist}")

	# Runs in 30 sec, output 7732

	return 0	

# make sure to send a COPY of keys_d in here if we don't want the main version modified
def dijkstra(arr, x_start, y_start, link_d, target_x, target_y):
	# Keep track of dependencies:
	# Keep track of each door we pass as we go along. Store in node.
	# In the min step of dijkstra, if we replace the min dist for a node, also replace the dependency list.
	# That way each node has a record of the keys needed to get there from the middle.

	NUM_LEVELS = 10000

	arr_visited = np.zeros(shape=(arr.shape[0], arr.shape[1], NUM_LEVELS))
	arr_visited[y_start,x_start,0] = 1

	arr_minDist = np.ones(shape=(arr.shape[0], arr.shape[1], NUM_LEVELS)) * np.inf
	arr_minDist[y_start,x_start,0] = 0

	came_from = dict()

	open_set = {(x_start, y_start, 0)}

	while len(open_set)>0:

		# choose node with least distance so far
		least_dist = np.inf
		least_x = None
		least_y = None
		least_level = None

		for pos in open_set:
			x = pos[0]
			y = pos[1]
			level = pos[2]

			if arr_minDist[y,x,level] < least_dist:

				least_dist = arr_minDist[y,x,level]
				least_x = x
				least_y = y
				least_level = level

		x = least_x
		y = least_y
		level = least_level

		## Check if we are at the goal node (have to terminate here, since this will go on forever otherwise)
		if (target_x, target_y, 0) == (x, y, level):

			print()
			print(f"Started at {(x_start, y_start, 0)}")
			print(f"Visited target {(target_x, target_y, 0)}")

			path = reconstruct_path(came_from, target_x, target_y, 0)

			return (arr_minDist, path) # should already be assigned

		dist_here = arr_minDist[y,x,level]
		dist_nbhrs_tmp = dist_here + 1

		neighbors = get_neighbors(arr, x, y, level, link_d)

		for n in neighbors:
			xx = n[0]
			yy = n[1]
			ll = n[2]
			is_warp = n[3]

			warp_penalty = 0
			if is_warp:
				warp_penalty = 1

			if dist_nbhrs_tmp + warp_penalty < arr_minDist[yy,xx,ll]:

				arr_minDist[yy,xx,ll] = dist_nbhrs_tmp + warp_penalty

				came_from[ (xx,yy,ll) ] = (x, y, level)

		unvisited_nhbrs = get_unvisited_neighbors(neighbors, arr_visited, arr_minDist) # return in ascending order of distance, so we can iterate

		# print(f"Evaluating {x}, {y}, {level} with unvisited neighbors {unvisited_nhbrs}")

		open_set.remove((x, y, level))
		arr_visited[y,x,level]=1

		for nhbr in unvisited_nhbrs:

			open_set.add( nhbr )
 
	return arr_minDist


def reconstruct_path(came_from, x, y, L):

	path = []
	state = (x, y, L)
	path.insert(0, (x, y, L))
	while (x, y, L) in came_from.keys():
		(x, y, L) = came_from[(x, y, L)]
		path.insert(0, (x, y, L))

	return path




def get_neighbors(arr, x, y, level, link_d):

	prospects = [(x+1,y,level),(x-1,y,level),(x,y+1,level),(x,y-1,level)]

	neighbors = []

	for p in prospects:
		xx = p[0]
		yy = p[1]
		LL = p[2]

		if xx<0 or xx>=arr.shape[1]:
			continue

		if yy<0 or yy>=arr.shape[0]:
			continue

		if not arr[yy,xx]=='.':
			continue

		is_warp = False
		final_level = LL

		if (xx, yy) in link_d.keys():

			# check that the portal is open, not blocked
			if is_valid_warp(arr, xx, yy, level, link_d):

				is_warp = True

				if is_outer_gate(arr, xx, yy, level, link_d):
					final_level = LL - 1
				else:
					final_level = LL + 1

				key = (xx, yy)

				xx = link_d[key][0]
				yy = link_d[key][1]

		neighbors.append((xx,yy,final_level,is_warp))

	return neighbors

# check that the portal is open, not blocked
def is_valid_warp(arr, xx, yy, level, link_d):

	if is_outer_gate(arr, xx, yy, level, link_d):

		if level >= 1:
			return True
		else:
			return False

	elif is_inner_gate(arr, xx, yy, level, link_d):

		return True

	return False

def is_outer_gate(arr, xx, yy, level, link_d):

	if not arr[yy,xx]=='.':
		return False

	XX = {2, arr.shape[1]-3}
	YY = {2, arr.shape[0]-3}

	if xx in XX or yy in YY:
		return True

	return False

def is_inner_gate(arr, xx, yy, level, link_d):

	if not arr[yy,xx]=='.':
		return False

	return True

def get_unvisited_neighbors(neighbors, arr_visited, arr_minDist):

	uv = []

	for n in neighbors:

		x = n[0]
		y = n[1]
		level = n[2]

		if arr_visited[y,x,level]==1:
			continue # visted

		uv.append( (x,y,level) )

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