from pandas import read_csv
import csv
import operator
from math import isnan
import numpy as np
import copy

def find_region(state_region, state):
	for entry in state_region:
		if entry[0] == state:
			return entry[1]

def dict_with_key_2nd(tup, di):
    for a, b in tup:
        di.setdefault(b, []).append(a)
    return di

def dict_with_key_1st(tup, di):
	for a, b in tup:
		di.setdefault(a, []).append(b)
	return di

def find_average(states_list, data, rows):
	avg_entry = np.zeros(rows)
	for row in range(rows):
		c = 0
		s = 0
		for st in states_list:
			if st in data.keys():
				# print(st)
				if not isnan(data[st][row]): 
					s = s + data[st][row]
					c = c+1
		if c = 0:
			avg_entry[row] = 0
		else:
			avg_entry[row] = s/c
	return avg_entry


data = csv.reader(open('Data/regions.csv'),delimiter = ',')
state_region = sorted(data, key = operator.itemgetter(1)) 

state_to_region = {}
region_to_states = {}
dict_with_key_1st(state_region,state_to_region)
dict_with_key_2nd(state_region,region_to_states)
del region_to_states['Region']


data = read_csv('Data/datagov/Economy/gross-domestic-product-gdp-constant-price.csv',delimiter = ',')
states = data.keys()
rows = len(data[states[10]])

average = copy.deepcopy(region_to_states)
for region in region_to_states.keys():
	average[region] = np.zeros(rows)
	states_list = region_to_states[region]
	print(states_list)
	average[region] = find_average(states_list, data, rows)
	# for st in st
print(average)


# print(states)
for state in states:
	# print(state)
	for da in data[state]:
		empty = False
		try:
			empty = isnan(da)
		except(TypeError, RuntimeError, NameError):
			pass
		if empty:
			# print(state)
			try:
				region = state_to_region[state]
				# print(state, region)
			except(KeyError):
				pass

