import argparse
import numpy as np

class GravNd:

	def __init__(self, myname):
		self.orb_targets = []
		self.orb_me = []
		self.name = myname
		self.visited = False


def get_args():

	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")

	return parser.parse_args()


def parse_orbit_input(fpath):

	f = open(fpath, 'r')
	lines = f.readlines()
	f.close()

	i=0
	L=len(lines)
	orb_d = dict() # name : gravNd

	for line in lines:

		line = line.strip()
		if ')' not in line:
			continue

		r = line.find(')')
		target_name = line[:r]
		orbiter_name = line[(r+1):]

		if not target_name in orb_d.keys():
			orb_d[target_name] = GravNd(target_name)
		
		orb_d[target_name].orb_me.append(orbiter_name)

		if not orbiter_name in orb_d.keys():
			orb_d[orbiter_name] = GravNd(orbiter_name)
		
		orb_d[orbiter_name].orb_targets.append(target_name)

	return orb_d


def find_san(orb_d, curr_Nd_name, end_Nd_name, traveled_dist):

	orb_d[curr_Nd_name].visited = True

	if curr_Nd_name == end_Nd_name:
		return traveled_dist

	possible_targets = orb_d[curr_Nd_name].orb_targets + orb_d[curr_Nd_name].orb_me
	possible_targets = [Nd for Nd in possible_targets if not orb_d[Nd].visited]

	target_dists = [np.inf]

	for targ_name in possible_targets:
		target_dists.append( find_san(orb_d, targ_name, end_Nd_name, traveled_dist + 1) )

	return min(target_dists)



def run_main():

	args = get_args()
	orb_d = parse_orbit_input(args.infile)

	start_Nd_name = orb_d["YOU"].orb_targets[0]
	end_Nd_name = orb_d["SAN"].orb_targets[0]

	distance = find_san(orb_d, start_Nd_name, end_Nd_name, 0)

	print(f"The minimum distance is: {distance}")

	return 0


if __name__=='__main__':

	run_main()