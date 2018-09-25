from pandas import read_csv
import csv
import operator
from math import isnan
import numpy as np
import copy
import os
import pandas as pd

#------------------------Choose Input File--------------------
Category = 'Economy'
file_list = ['gross-domestic-product-gdp-constant-price.csv',
'gross-domestic-product-gdp-current-price.csv',
'state-wise-net-domestic-product-ndp-constant-price.csv',
'state-wise-net-domestic-product-ndp-current-price.csv']

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

	#Used to give back state from encoded state
	#Gives same if not found
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


	def filter_data(data_full):
		cols = data_full.keys()
		states = state_to_region.keys()
		rows = len(data_full[cols[0]])
		new_col = np.zeros(rows)
		new_col[:] = np.nan
		a = 1
		for state in states:
			if state_not_in_data(state, cols):
				data_full[defilter_state(state)] = new_col


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

	def get_states(state_region):
		state_list = ['India']
		for index,element in enumerate(state_region):
			if not index ==0:
				state_list = np.hstack((state_list, element[0]))
		state_list[1:].sort()#India at top then sorted
		return state_list

	file_in = os.path.join('Data/datagov',Category,file_name)
	file_ou = os.path.join('Out_1a/datagov',Category)
	data = read_csv(file_in ,delimiter = ',')

	states = data.keys()
	filter_data(data)
	rows = len(data[states[0]])

	average = copy.deepcopy(region_to_states)
	for region in region_to_states.keys():
		average[region] = np.zeros(rows)
		states_list = region_to_states[region]
		average[region] = find_average(region, data, rows)
		
	average['ind'] = find_national(average, rows)

	for region in region_to_states.keys():
		for i, entry in enumerate(average[region]):
				if entry == 0:
					average[region][i] = average['ind'][i]

	for x in data:
		if (filter_word(x) in state_to_region):
			empty_signal = [False] * rows
			index = 0
			for entry in data[x]:
				if is_empty(entry):
					empty_signal[index] = True
			data[x] = np.where(np.isnan(data[x]), average[state_to_region[filter_word(x)][0]], data[x])
			index += 1
	#-------------------Uniform State Names-----------------------
	a = data.values
	keys = data.keys().values
	for i,key in enumerate(keys):
		keys[i] = defilter_state(filter_word(key),key)


	#-------------------------------------------------------------

	# with open(os.path.join(file_ou, file_name),'w') as f:
	# 	data.to_csv(f,header = True)
	# print("Output_file stored at-'", os.path.join(file_ou, file_name),"'")

	year_in = np.where(keys == 'Duration')[0][0]
	for i,key in enumerate(keys):
		if 'Item' in key:
			category_in = i
			break
	# category_in = np.where(keys== 'Items Description' or keys == "Items  Description")[0][0]
	for i in range(a.shape[0]):
		a[i,category_in] = a[i,category_in] + a[i,year_in]
	a = np.delete(a,year_in,axis=1)
	keys = np.delete(keys, year_in)

	#-------------------
	new_keys = a[:,0]

	a = np.vstack((keys,a))
	a = np.transpose(a)
	a = np.delete(a,0, axis = 0)
	new_keys = np.hstack((['state'], new_keys))
	if is_empty(new_keys[len(new_keys)-1]):
		# print(new_keys.shape)
		new_keys = new_keys[0:-1]
		a = np.delete(a, a.shape[1]-1,axis=1)


	def sort_states(a):
		keys = new_keys
		state_list = get_states(state_region)
		for index, state in enumerate(state_list):
			state_index = np.where(a[:,np.where(keys=='state')[0][0]] == state)
			temp = np.copy(a[state_index[0],:])
			if index == 0:
				b = temp
			else:
				b = np.vstack((b,temp))
		return b

	# print(a.shape)
	a= sort_states(a)
	#-------------------
	dat_fr = pd.DataFrame(a, columns = new_keys)
	with open(os.path.join(file_ou, file_name),'w') as f:
		dat_fr.to_csv(f)
	print("Output_file stored at-'", os.path.join(file_ou, file_name),"'")
