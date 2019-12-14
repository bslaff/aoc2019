import argparse
import numpy as np
import math

class Node:

	def __init__(self, name, elements, counts, parents, children):
		self.name = name
		self.elements = elements
		self.counts = counts
		self.parents = parents
		self.children = children
		self.is_resolved = False

def get_args():

	parser = argparse.ArgumentParser()
	parser.add_argument("infile", type=str, help="Path to the input file")
	
	return parser.parse_args()

def get_rules(args):

	f = open(args.infile, 'r')
	lines = f.readlines()
	f.close()

	d = dict()

	for line in lines:
		if "=>" not in line:
			continue

		line = line.split("=>")

		prod = line[1]
		prod = prod.strip()
		while "  " in prod:
			prod = prod.replace("  ", " ")
		prod = prod.split(" ")

		prod_element = prod[1]
		prod_count = int(prod[0])

		reactants = line[0]
		reactants = reactants.strip()
		while "  " in reactants:
			reactants = reactants.replace("  ", " ")
		reactants = reactants.split(",")
		reactants = [v.strip().split(" ") for v in reactants]

		elements = []
		counts = []
		
		for r in reactants:
			count = int( r[0].strip() )
			ele = r[1].strip()
			elements.append(ele)
			counts.append(count)

		elements.append(prod_element)
		counts.append(prod_count) # product is the last in these arrays

		counts = np.asarray(counts)

		d[prod_element] = dict()

		node = Node(prod_element, elements, counts, set(), set(elements[:-1]) )
		d[prod_element] = node

	## ORE case, never a product
	node = Node("ORE", ["ORE"], [1], set(), set())
	d["ORE"] = node

	return d

def set_parents(nodes_d):

	for name in nodes_d.keys():

		for child_name in nodes_d[name].children:
			if name not in nodes_d[child_name].parents:
				nodes_d[child_name].parents.add(name)

	return None

def get_idxs(nodes_d):

	d = dict()
	i=0
	for k in list(nodes_d.keys()):
		d[k]=int(i)
		i+=1
	return d

def compute_min_inputs(count_arr, nodes_d, idx_d, prod_ele):

	if prod_ele=="ORE":
		nodes_d[prod_ele].is_resolved = True
		return None

	rx_elements = nodes_d[prod_ele].elements
	rx_counts = nodes_d[prod_ele].counts.copy()

	needed_prod_count = count_arr[ idx_d[prod_ele] ]
	prod_rule_count = rx_counts[-1]

	rx_factor = math.ceil(needed_prod_count / prod_rule_count)

	for i in range(len(rx_elements)-1):

		count = rx_counts[i]
		ele = rx_elements[i]

		count_arr[ idx_d[ele] ] += int(count*rx_factor)

	count_arr[ idx_d[prod_ele] ] = 0
	nodes_d[prod_ele].is_resolved = True

	return None

def print_nodes_dict(nodes_d):

	for k in nodes_d.keys():

		n = nodes_d[k].name
		e = nodes_d[k].elements
		c = nodes_d[k].counts
		p = nodes_d[k].parents
		ch = nodes_d[k].children
		r = nodes_d[k].is_resolved

		print(f"k: {n}, {e}, {c}, {p}, {ch}, {r}")

	return None


def run_main():

	args = get_args()
	nodes_d = get_rules(args)
	set_parents(nodes_d)
	# print_nodes_dict(nodes_d)
	idx_d = get_idxs(nodes_d)

	L = len(idx_d.keys())
	count_arr = np.zeros(L)

	count_arr[ idx_d["FUEL"] ] = 1

	while not nodes_d["ORE"].is_resolved:

		for name in nodes_d.keys():

			if nodes_d[name].is_resolved:
				continue

			can_now_resolve = True
			for p_name in nodes_d[name].parents:
				can_now_resolve = nodes_d[p_name].is_resolved # if any False, turns us False
				if not can_now_resolve:
					break # if ever false we are done

			if can_now_resolve:
				compute_min_inputs( count_arr, nodes_d, idx_d, name )

	min_ore = int( count_arr[ idx_d["ORE"] ] )
	print(f"ORE required: {min_ore}")

	return 0


if __name__=="__main__":

	run_main()