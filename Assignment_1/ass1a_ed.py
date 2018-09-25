from pandas import read_csv
import csv
import operator
from math import isnan
import numpy as np
import copy
import os
import pandas as pd

#------------------------Choose Input File--------------------
Category = 'Education'
file_list = ['drop-out-rate.csv',
'gross-enrolment-ratio-higher-education.csv',
'gross-enrolment-ratio-schools.csv',
'literacy-rate-7-years.csv',
'percentage-schools-boys-toilet.csv',
'percentage-schools-computers.csv',
'percentage-schools-drinking-water.csv',
'percentage-schools-electricity.csv',
'percentage-schools-girls-toilet.csv']

file_alias_list = ['_dropout','_high_ed','_schools','_literacy',
'_b_toilet','_computers','_water','_electricity','_g_toilet']


for file_index,file_name in enumerate(file_list):
	file_alias = file_alias_list[file_index]
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

	def defilter_state(filtered, original='col'):
		for pair in state_region:
			if filter_word(pair[0]) == filtered:
				return pair[0]
		if 'india' in original.lower():
			return 'India'
		return original


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


	def find_average(data, category, rows, year):
		i = 0
		avg = 0
		entry = -100
		c = 0
		while(i<rows):
			if not is_empty(data[category][i]):
				try:
					entry = float(data[category][i])
				except ValueError:
					pass
				if (not entry == -100) and data['year'][i]==year:
					avg = avg + entry
					c += 1
					entry = -100
			i += 1
		avg/=c
		return avg


	def find_national(data, year, category, l):
		i = 0;
		while(not(filter_word(data['state'][i]) == filter_word('India') and data['year'][i] == year) and i < l):
			i += 1
		if not is_empty(data[category][i]):
			return float(data[category][i])
		else:
			return 0


	def get_states(state_region):
		state_list = ['India']
		for index,element in enumerate(state_region):
			if not index ==0:
				state_list = np.hstack((state_list, element[0]))
		state_list[1:].sort()#India at top then sorted
		return state_list

	file_in = os.path.join('Data/datagov',Category,file_name)
	file_ou = os.path.join('Out_1a/datagov',Category)
	#---------------------Main Code comes here---------------------

	data = csv.reader(open('Data/regions.csv'),delimiter = ',')
	state_region = sorted(data, key = operator.itemgetter(1)) # list of states with their regions
	# print(state_region)
	state_list = get_states(state_region)
	state_to_region = {}
	region_to_states = {}
	dict_with_key_1st(state_region,state_to_region)
	dict_with_key_2nd(state_region,region_to_states)
	del region_to_states['reg']
	state_to_region['ind'] = ['ind']
	region_to_states['ind'] = ['ind']

	# print(state_to_region)
	# print(region_to_states)



	data = read_csv(file_in ,delimiter = ',')
	filter_data(data)
	a = data.keys()
	rows = len(data[a[0]])
	empty_signal = np.zeros(rows)
	fillers = np.zeros(rows)
	for i in a:
		column_i =  data[i].values
		index = 0
		for entry in column_i:
			if is_empty(entry):
				empty_signal[index] = 1
				reg = state_to_region[filter_word(data['state'][index])]
				# print(reg)
				if reg[0] == 'ind':
					# print(data['state'][index], data['year'][index], i)
					column_i[index] = find_average(data, i , rows, data['year'][index])
					index += 1
					continue
				c = 0
				s = 0
				for j in range(rows):
					if state_to_region[filter_word(data['state'][j])] == reg and data['year'][index] == data['year'][j] and not is_empty(data[i][j]):
						en = 0
						try:
							en = float(data[i][j])
						except(ValueError):
							pass 
						if not en==0:
							c += 1
							s += en
				if c == 0:
					column_i[index] = find_average(data, i, rows, data['year'][index])
				else:
					column_i[index] = s/c
			index += 1
		data[i] = np.where(empty_signal, column_i, data[i])

	print("Output_file stored at-'", os.path.join(file_ou, file_name),"'")
	with open(os.path.join(file_ou, file_name),'w') as f:
		data.to_csv(f,header = True)
	# print(rows)
	#--------------Post Processing----------------------
	dat = read_csv(os.path.join(file_ou, file_name) ,delimiter = ',')
	a = dat.values
	a = np.delete(a,0,axis =1)
	keys = data.keys().values

	def fix_telangana(a):
		if 'year' in keys:
			rows = a.shape[0]
			rem = 37 - rows % 37
			andhra_index = np.where(a[:,np.where(keys=='state')[0][0]] == 'Andhra Pradesh')[0]
			andhra_years = a[:,np.where(keys=='year')[0][0]][andhra_index]
			for i, yr in enumerate(andhra_years):
				andhra_years[i] = yr[0:4]
			andhra_years = andhra_years.astype(np.float)
			req_index = np.argsort(andhra_years)[0:rem]
			for i in req_index:
				temp = np.copy(a[andhra_index[i],:])
				temp[np.where(keys=='state')[0][0]] = 'Telangana'
				a = np.vstack((a,temp))
		else:
			rows = a.shape[0]
			rem = 37 - rows % 37
			if rem == 1:
				andhra_index = np.where(a[:,np.where(keys=='state')[0][0]] == 'Andhra Pradesh')[0]
				temp = np.copy(a[andhra_index,:])
				x = np.where(keys=='state')[0][0]
				temp[0,x] = 'Telangana'
				a = np.vstack((a,temp))

		return a


	def fix_names(a):
		state_index = np.where(keys=='state')[0][0]
		for i in range(a.shape[0]):
			a[i,state_index] = defilter_state(filter_word(a[i,state_index]), a[i,state_index])
		return a
		

	def add_year_to_keys(year):
		ch_keys = np.copy([keys[0:-2]])
		for index in range(len(ch_keys)):
			ch_keys[index] = ch_keys[index] + year
		return ch_keys
	def change_structure(a):
		n_yr = a.shape[0]/37
		if n_yr>1:
			for index, state in enumerate(state_list):
				state_index = np.where(a[:,np.where(keys=='state')[0][0]] == state)[0]
				state_years = a[:,np.where(keys=='year')[0][0]][state_index]
				temp = [state]
				for row_no in state_index:
					temp = np.hstack((temp, np.copy(a[row_no,0:-2])))
				if index == 0:
					b = temp
				else:
					b = np.vstack((b,temp))
			new_keys = ['state']
			for index,year in enumerate(state_years):
				new_keys = np.hstack((new_keys,np.squeeze(add_year_to_keys(year))))
			# print(b.shape, new_keys.shape)
			return b,new_keys
		else:
			for index, state in enumerate(state_list):
				state_index = np.where(a[:,np.where(keys=='state')[0][0]] == state)
				temp = np.copy(a[state_index[0],1:])
				if index == 0:
					b = temp
				else:
					b = np.vstack((b,temp))
			new_keys = keys[1:]
			col_index = np.argsort(range(b.shape[1]))-1
			b = b[:,col_index]
			new_keys = keys[col_index]
			return b,new_keys


	def add_alias(new_keys):
		for index in range(len(new_keys)):
			new_keys[index] = new_keys[index] + file_alias
		return new_keys


	a = fix_telangana(a)
	a = fix_names(a)
	a,new_keys = change_structure(a)
	new_keys = add_alias(new_keys)
	# print(a,new_keys)

	dat_fr = pd.DataFrame(a, columns = new_keys)


	with open(os.path.join(file_ou, file_name),'w') as f:
		dat_fr.to_csv(f)