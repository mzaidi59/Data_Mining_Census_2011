from pandas import read_csv
import csv
import operator
from math import isnan
import numpy as np
import copy
import os

def filter_word(a):
	if a[0:3] == 'A &' or a[0:4] == 'Anda':
		b = 'ANI'
	elif a[0:3] == 'D &':
		b = 'Dadra & Nagar Haveli' 
	elif a == 'Uttar Pradesh':
		b = 'UPA'
	elif a[0:3] == 'NCT':
		b = 'Delhi'
	elif 'india' in a.lower():
		b = 'India'
	elif 'pon' in a.lower():
		b = 'Pud'
	else:
		b = a
	b = b.lower()
	return b[0:3]



def is_empty(entry):
	no_entry = False
	try:
		no_entry = isnan(entry)
	except(TypeError):
		pass
	if no_entry:
		return no_entry

	try:
		no_entry = (entry == 0.0)
	except(TypeError):
		pass
	if no_entry:
		return no_entry

	try:
		no_entry = np.isclose(entry, 0.0)
	except(TypeError):
		pass
	if no_entry:
		return no_entry

	try:
		no_entry = entry == '@' or entry == 'NA' or entry == 'NR' or entry.lower() == 'nan' or 'Uppe' in entry or entry == '0'
	except(AttributeError):
		pass

	return no_entry


def filter_data(data):
	a = data.keys()
	for i in a:
		if 'state' in i.lower():
			data['state'] = data.pop(i)
		if 'year' in i.lower():
			data['year'] = data.pop(i)


def dict_with_key_2nd(tup, di):
	for a, b in tup:
		a = filter_word(a)
		b = filter_word(b)
		di.setdefault(b, []).append(a)
	return di


def dict_with_key_1st(tup, di):
	for a, b in tup:
		a = filter_word(a)
		b = filter_word(b)
		di.setdefault(a, []).append(b)
	return di




data = csv.reader(open('Data/regions.csv'),delimiter = ',')
state_region = sorted(data, key = operator.itemgetter(1)) 

print(state_region,len(state_region))

state_to_region = {}
region_to_states = {}
dict_with_key_1st(state_region,state_to_region)
dict_with_key_2nd(state_region,region_to_states)
del region_to_states['reg']
state_to_region['ind'] = ['ind']
region_to_states['ind'] = ['ind']

print(state_to_region,len(state_to_region.keys()))
print(region_to_states)

Category = 'Economy'
# file_name = 'gross-domestic-product-gdp-constant-price.csv'
# file_name = 'gross-domestic-product-gdp-current-price.csv'
# file_name = 'state-wise-net-domestic-product-ndp-constant-price.csv'
file_name = 'state-wise-net-domestic-product-ndp-current-price.csv'

# Category = 'Demography'
# file_name = 'child-sex-ratio-0-6-years.csv'
# file_name = 'decadal-growth-rate.csv'
# file_name = 'sex-ratio.csv'

# Category = 'Education'
# file_name = 'drop-out-rate.csv'
# file_name = 'gross-enrolment-ratio-higher-education.csv'
# file_name = 'gross-enrolment-ratio-schools.csv'
# file_name = 'literacy-rate-7-years.csv'
# file_name = 'percentage-schools-boys-toilet.csv'
# file_name = 'percentage-schools-computers.csv'
# file_name = 'percentage-schools-drinking-water.csv'
# file_name = 'percentage-schools-electricity.csv
# file_name = 'percentage-schools-girls-toilet.csv'


def is_state(entry):
	a = region_to_states.keys()
	for i in a:
		if entry in region_to_states[i]:
			return True
	return False

def find_average(region, data, rows):
	avg_entry = np.zeros(rows)
	for row in range(rows):
		c = 0
		s = 0
		for ke in data.keys():
			# if is_state(filter_word(ke)) :
			# 			print(state_to_region[filter_word(ke)], filter_word(region))
			if is_state(filter_word(ke)) and state_to_region[filter_word(ke)][0] == filter_word(region) and (not is_empty(data[ke][row])):
				s = s + data[ke][row]
				c = c+1
		if c == 0:
			avg_entry[row] = 0
		else:
			avg_entry[row] = s/c
	return avg_entry


def find_national(average,rows):
	avg = np.zeros(rows)
	c = 0
	for reg in average:
		if not reg == 'ind':
			avg = avg + average[reg]
			c +=1
	avg/=c
	return avg

file_in = os.path.join('Data/datagov',Category,file_name)
file_ou = os.path.join('Out_1a/datagov',Category)
data = read_csv(file_in ,delimiter = ',')

states = data.keys()
rows = len(data[states[0]])

average = copy.deepcopy(region_to_states)
for region in region_to_states.keys():
	average[region] = np.zeros(rows)
	states_list = region_to_states[region]
	# print(states_list)
	average[region] = find_average(region, data, rows)
	# for st in st
# print(average)
# print(find_national(average, rows))
average['ind'] = find_national(average, rows)



for x in data:
	if (filter_word(x) in state_to_region):
		data[x] = np.where(np.isnan(data[x]), average[state_to_region[filter_word(x)][0]], data[x])
# print(data)

with open(os.path.join(file_ou, file_name),'w') as f:
	data.to_csv(f,header = True)

# for state in states:
# 	# print(state)
# 	r = 0
# 	for da in data[state]:
# 		empty = False
# 		try:
# 			empty = isnan(da)
# 		except(TypeError, RuntimeError, NameError):
# 			pass
# 		if empty:
# 			# print(state)
# 			if state in state_to_region.keys():
# 				region = state_to_region[state]
# 				print(state, region)
# 				print(data[state][r])

		# r = r + 1

# print(data)

