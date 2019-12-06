import argparse

class GravNd:

	def __init__(self, myname):
		self.orb_targets = []
		self.orb_me = []
		self.name = myname


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


def count_orbits_for(Nd, orb_d, this_Nd_n_orbits):

	to_add = 0

	for orb_me_Nd in Nd.orb_me:
		to_add += count_orbits_for(orb_d[orb_me_Nd], orb_d, this_Nd_n_orbits+1)

	return this_Nd_n_orbits + to_add



def run_main():

	args = get_args()
	orb_d = parse_orbit_input(args.infile)
	total = count_orbits_for(orb_d["COM"], orb_d, 0)

	print(f"The total is: {total}")

	return 0


if __name__=='__main__':

	run_main()