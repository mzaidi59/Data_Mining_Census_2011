from pandas import read_csv
import csv
import operator
from math import isnan
import numpy as np
import copy
import os
from matplotlib import *
import pandas as pd

#------------------------Choose Input File--------------------
Category = 'Demography'
file_list = ['child-sex-ratio-0-6-years.csv',
'decadal-growth-rate.csv',
'sex-ratio.csv']

for file_name in file_list:
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

	state_to_region = {}
	region_to_states = {}
	dict_with_key_1st(state_region,state_to_region)
	dict_with_key_2nd(state_region,region_to_states)
	del region_to_states['reg']
	del state_to_region['sta']
	state_to_region['ind'] = ['ind']
	region_to_states['ind'] = ['ind']

	# print(state_to_region,len(state_to_region.keys()))
	# print(region_to_states)

	def defilter_state(filtered, original='col'):
		for pair in state_region:
			if filter_word(pair[0]) == filtered:
				return pair[0]
		if 'india' in original.lower():
			return 'India'
		return original


	def state_not_in_data(state, cols):
		for col in cols:
			if filter_word(col) == state:
				return False
		return True

	def filter_data(data):
		a = data.keys()
		for i in a:
			if 'state' in i.lower():
				data['state'] = data.pop(i)
			if 'year' in i.lower():
				data['year'] = data.pop(i)

	file_in = os.path.join('Data/datagov',Category,file_name)
	file_ou = os.path.join('Out_1a/datagov',Category)
	data = read_csv(file_in ,delimiter = ',')

	filter_data(data)
	states = data['state'].values
	if defilter_state('tel') not in data['state']:
			index = np.where(states == defilter_state('and'))
	# print(index)

	a = data.values
	b = a[index[0],:]
	a = np.vstack((a,b))

	keys = data.keys()
	index = np.where(keys == 'state')

	a[a.shape[0]-1,index[0][0]] = defilter_state('tel')
	# print(a)
	filter_data(data)
	# print(type(keys))
	# print(a.shape)
	# print(type(a))


	index = np.where(data.keys().values == 'state')[0][0]
	# print(index)
	for i in range(a.shape[0]):
		a[i,index] = defilter_state(filter_word(a[i,index]),a[i,index])
	# print(a[:,index], a[3,index])

	def get_states(state_region):
		state_list = ['India']
		for index,element in enumerate(state_region):
			if not index ==0:
				state_list = np.hstack((state_list, element[0]))
		state_list[1:].sort()#India at top then sorted
		return state_list
		# 
	def sort_states(a):
		state_list = get_states(state_region)
		for index, state in enumerate(state_list):
			state_index = np.where(a[:,np.where(keys=='state')[0][0]] == state)
			temp = np.copy(a[state_index[0],:])
			if index == 0:
				b = temp
			else:
				b = np.vstack((b,temp))
		return b
	# print(a,keys)
	a = numpy.delete(a,0,axis = 1)
	keys = keys[1:]
	# print(a,keys)
	col_index = np.argsort(range(a.shape[1]))-1
	a = a[:,col_index]
	keys = keys[col_index]

	a = sort_states(a)
	# print(a,keys)

	dat_fr = pd.DataFrame(a, columns = keys)

	with open(os.path.join(file_ou, file_name),'w') as f:
		dat_fr.to_csv(f)
	print("Output_file stored at-'", os.path.join(file_ou, file_name),"'")


