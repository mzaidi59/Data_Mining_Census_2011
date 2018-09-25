from pandas import read_csv
import csv
import operator
from math import isnan, log10, floor, ceil
import numpy as np
import copy
import os
from matplotlib import *
import pandas as pd
from scipy import spatial
import random
import matplotlib.pyplot as plt

#Variables
h_m = 10 #for relief algorithm
corr_thresh = 0.97

file_ou = os.path.join('Out_1b/datagov')


def read_data(file_in):
	data = read_csv(file_in ,delimiter = ',')
	np_data = data.values
	file_keys = data.keys().values
	np_data = np.delete(np_data, 0 ,axis = 1)
	file_keys = file_keys[1:]
	return np_data, file_keys


def merge_files(category, files, in_path, ou_path):
	for index, file in enumerate(files):
		file_in = os.path.join(in_path,category,file)
		np_data, file_keys = read_data(file_in)

		if index == 0:
			m_data = np_data
			m_keys = file_keys
		else:
			m_data = np.hstack((m_data, np_data[:,1:]))
			m_keys = np.hstack((m_keys, file_keys[1:]))
	dat_fr = pd.DataFrame(m_data, columns = m_keys)
	with open(os.path.join(ou_path,category+'_merged.csv'),'w') as f:
		dat_fr.to_csv(f)
		
def find_closest(data_np):
	rpr = np.zeros((1,data_np.shape[0]))
	for i in range(data_np.shape[0]):
		# rpr[0,i] = 1 - spatial.distance.cosine(data_np[0,:],data_np[i,:])
		rpr[0,i] = numpy.sqrt(numpy.sum((data_np[0,:]-data_np[i,:])**2))
	ranks = np.argsort(rpr[0,:])
	return ranks

def normalized(a, axis=-1, order=2):
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2==0] = 1
    return a / np.expand_dims(l2, axis)



Category = ['Demography', 'Economy','Education','data']
file_names = {Category[0]:[
'child-sex-ratio-0-6-years.csv',
'decadal-growth-rate.csv',
'sex-ratio.csv'],
Category[1]:[
'gross-domestic-product-gdp-constant-price.csv',
'gross-domestic-product-gdp-current-price.csv',
'state-wise-net-domestic-product-ndp-constant-price.csv',
'state-wise-net-domestic-product-ndp-current-price.csv'],
Category[2]:[
'drop-out-rate.csv',
'gross-enrolment-ratio-higher-education.csv',
'gross-enrolment-ratio-schools.csv',
'literacy-rate-7-years.csv',
'percentage-schools-boys-toilet.csv',
'percentage-schools-computers.csv',
'percentage-schools-drinking-water.csv',
'percentage-schools-electricity.csv',
'percentage-schools-girls-toilet.csv'],
Category[3]:[
'Demography_merged.csv',
'Economy_merged.csv',
'Education_merged.csv']}

for categ in Category[0:-1]:
	in_path = os.path.join('Out_1a/datagov')
	ou_path = os.path.join(file_ou,'data')
	merge_files(categ, file_names[categ],in_path, ou_path)

in_path = os.path.join('Out_1b/datagov')
ou_path = os.path.join('Out_1b/datagov/data')
merge_files(Category[-1],file_names[Category[-1]],in_path, ou_path)

full_dat_path = os.path.join('Out_1b/datagov/data',Category[-1]+'_merged.csv')
data_np, keys = read_data(full_dat_path)
float_data = data_np[:,1:].astype(float)
rank_1 = find_closest(float_data)
# print("------------Question_2------------")
print("Before_Normalisation",data_np[rank_1[1:6],0])
float_data_norm = normalized(float_data,1)
rank_1 = find_closest(float_data_norm)
print("Post_Normalisation",data_np[rank_1[1:6],0])
float_data_norm = normalized(float_data,0)
# Category = ['data']

for ind_cate,categ in enumerate(Category):
	print("---------",categ,"--------")
	full_dat_path = os.path.join('Out_1b/datagov/data',categ+'_merged.csv')
	data_np, keys = read_data(full_dat_path)
	float_data = data_np[:,1:].astype(float)
	float_data_norm = normalized(float_data,0)
	#3rd______________________________________________________________
	# finding NxN correlation matrix 
	# print("--Question_3--")
	def find_correlation(float_data_norm):
		n_vect = float_data_norm.shape[1]
		corr_matrix = np.zeros((n_vect,n_vect))
		for i in range(n_vect):
			for j in range(n_vect):
				a = float_data_norm[:,i]
				b = float_data_norm[:,j]
				corr_matrix[i,j] = np.corrcoef(a,b)[1,0]
		c = 0
		for i in range(n_vect):
			for j in range(i):
				# print(i,j,corr_matrix[i,j])
				if corr_matrix[i,j] > corr_thresh:
					c += 1
		print(c, 'pairs of features highly correlated')
		return corr_matrix

	corr_matrix = find_correlation(float_data_norm)
	# print(corr_matrix)
	#4th______________________________________________________________
	#to find region label array
	# print("--Question_4--")
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

	data_regions = csv.reader(open('Data/regions.csv'),delimiter = ',')
	state_region = sorted(data_regions, key = operator.itemgetter(1)) 
	state_to_region = {}
	region_to_states = {}
	dict_with_key_1st(state_region,state_to_region)
	dict_with_key_2nd(state_region,region_to_states)
	del region_to_states['reg']
	del state_to_region['sta']
	state_to_region['ind'] = ['ind']
	region_to_states['ind'] = ['ind']

	def encode_region(states):
		regions = np.array(list(region_to_states.keys()))
		y = np.zeros((1,len(states)))
		for index,state in enumerate(states):
			y[0,index] = np.where(regions == state_to_region[filter_word(state)])[0][0]
		return np.squeeze(y)


	states = data_np[1:,0]
	X = float_data_norm[1:,:]
	y = encode_region(states)

	def nearest_hit(X,indices,feature,state):
		minim = 1e10
		for index in indices:
			if not index == state:
				dmin = numpy.sqrt(numpy.sum((X[index,:]-X[state,:])**2))
				if dmin<minim:
					minim = dmin
					diff = abs(X[index,feature]-X[state,feature])
		return diff

	def nearest_miss(X,indices,feature,state):
		minim = 1e10
		for index in range(X.shape[0]):
			if not index in indices:
				dmin = numpy.sqrt(numpy.sum((X[index,:]-X[state,:])**2))
				if dmin<minim:
					diff = abs(X[index,feature]-X[state,feature])
					minim = diff
		return diff


	def relief_ranking(m,X,y):
		region_dict = {}
		n_objects = X.shape[0]
		n_features = X.shape[1]
		features_scores = np.zeros(n_features)
		for i in range(max(y.astype(int))+1):
			region_dict[i] = np.where(y==i)[0]
		for i in range(n_features):
			for j in range(m):
				random_object = random.randint(0,n_objects-1)
				indices = region_dict[y[random_object]]
				features_scores[i] = features_scores[i] - nearest_hit(X,indices,i,random_object) + nearest_miss(X,indices,i,random_object)
		return np.argsort(features_scores)

	feature_ranking = relief_ranking(h_m,X,y)
	# print("--Question_5--")
	print(keys[feature_ranking[-2:]])
	a = feature_ranking[-2:]
	# print(a)
	#-5th, given best features plot them
	v1 = X[:,a[0]]
	v2 = X[:,a[1]]
	fig = plt.figure(categ)
	plt.scatter(v1,v2)
	q =np.linspace(0,100,101)
	plt.scatter(np.percentile(v1,q),np.percentile(v2,q))
	fig.suptitle('2D Scatter and Q-Q Plots of Best 2 Features for Full '+ categ)
	plt.xlabel('Feature_1')
	plt.ylabel('Feature_2')
	fig.show()

	#6th_part_Intuitive_Partitioning
	# print("--Question_6--")

	def roundup(x,y):
		return int(ceil(x / 10**y)) * 10**y

	def rounddown(x,y):
		return int(floor(x / 10**y)) * 10**y

	def add_part(part, index, add):
		part = np.hstack

	def add_partition(part):
		n_part = {1:5,2:4,3:3,4:4,5:5,6:3,7:3,8:4,9:3}
		new_part = part
		index = 0
		add = [0,0,0,0,0]
		while index < len(part) - 1:
			x = part[index+1]
			y = part[index]
			differ = abs(int(str(abs(x-y))[0]))
			diff = n_part[differ]
			add[0:diff] = [int((part[index+1]-part[index]))/diff]*diff
			if differ == 7:
				add[0] = 2*int((part[index+1]-part[index]))/7
				add[1] = 3*int((part[index+1]-part[index]))/7
			for i in range(diff-1):
				part = np.hstack((part[:index+1],[part[index]+add[i]],part[index+1:]))
				index += 1
			index += 1
		return part

	def intuitive_partition(vec):
		#length 37 assumed
		print(vec)
		outlier = [vec[0],vec[1],vec[-2],vec[-1]]
		vec = vec[2:len(vec)-2]
		a = floor(log10(abs(min(vec))))
		b = max(a,floor(log10(abs(max(vec)))))
		part = [rounddown(min(vec),b), roundup(max(vec),b)]
		part = add_partition(part)
		print(part)
		left_part = rounddown(outlier[0], b)
		left = rounddown(outlier[0], floor(log10(abs(outlier[0]))))

		if not part[1] == 0:
			if left_part < part[0]:
				part = np.hstack((left_part,part))
		else:
			if left_part < part[0]:
				part = np.hstack((left_part,part))
			else:
				part = np.hstack((left,part))
		right_part = roundup(outlier[3], b)
		if right_part > part[-1]:
			part = np.hstack((part,right_part))
		part = add_partition(part)

		print(part)
		return part
		
	v1 = np.sort(float_data[:,a[0]])
	v2 = np.sort(float_data[:,a[1]])
	# a = [-351,-300,-159,0,200,1000,1838,2500,4700]
	partion1 = intuitive_partition(v1)
	partion2 = intuitive_partition(v2)
	print(corr_matrix[a[0],a[1]], 'is correlation between best 2 features')

plt.show() 
