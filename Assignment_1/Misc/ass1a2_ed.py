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


#------------------------Choose Input File--------------------
Category = 'Education'
# file_name = 'drop-out-rate.csv'
# file_name = 'gross-enrolment-ratio-higher-education.csv'
# file_name = 'gross-enrolment-ratio-schools.csv'
# file_name = 'literacy-rate-7-years.csv'
# file_name = 'percentage-schools-boys-toilet.csv'
# file_name = 'percentage-schools-computers.csv'
# file_name = 'percentage-schools-drinking-water.csv'
# file_name = 'percentage-schools-electricity.csv'
file_name = 'percentage-schools-girls-toilet.csv'

file_in = os.path.join('Data/datagov',Category,file_name)
file_ou = os.path.join('Out_1a/datagov',Category)
#---------------------Main Code comes here---------------------

data = csv.reader(open('Data/regions.csv'),delimiter = ',')
state_region = sorted(data, key = operator.itemgetter(1)) # list of states with their regions


state_to_region = {}
region_to_states = {}
dict_with_key_1st(state_region,state_to_region)
dict_with_key_2nd(state_region,region_to_states)
del region_to_states['reg']
state_to_region['ind'] = ['ind']
region_to_states['ind'] = ['ind']

print(state_to_region)
print(region_to_states)



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
print(rows)




