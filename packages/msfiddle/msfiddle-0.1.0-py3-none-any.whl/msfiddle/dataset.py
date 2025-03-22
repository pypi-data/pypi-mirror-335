import re
import copy
import pickle
from pyteomics import mgf
from tqdm import tqdm
import numpy as np
from decimal import *
import pandas as pd
import math
from copy import deepcopy
import torch
from torch.utils.data import Dataset

from .utils import ATOMS_INDEX, generate_ms, parse_collision_energy, unify_precursor_type, formula_to_dict, formula_to_vector



# Used for testing
class MGFDataset(Dataset):
	def __init__(self, path, encoder): 
		self.data = []
		self.general_filter_config = {
			'min_mz': 50, 
			'max_mz': 1500, 
			'min_peak_num': 5, 
		}
		self.use_simulated_precursor_mz = encoder['use_simulated_precursor_mz']
		if self.use_simulated_precursor_mz: 
			self.precursor_mz_key = 'simulated_precursor_mz'
		else:
			self.precursor_mz_key = 'precursor_mz'
		
		# read data from mgf file
		spectra = mgf.read(path)
		print(len(spectra), 'spectra loaded from', path)
		
		# filter out invalid data (add the other rules if needed)
		spectra, _ = self.filter_spec(spectra, self.general_filter_config, type2charge=encoder['type2charge'])
		print(len(spectra), 'spectra left after filtering')

		# convert mgf to pkl
		self.load_mgf_spectra(spectra, encoder)
		print(len(self.data), 'spectra loaded into the dataset')

	def __len__(self): 
		return len(self.data)

	def __getitem__(self, idx): 
		return self.data[idx]['title'], self.data[idx]['precursor_type'], self.data[idx]['spec'][:, 0], self.data[idx]['env'], self.data[idx]['neutral_add']
		
	def filter_spec(self, spectra, general_filter_config, type2charge): 
		clean_spectra = []
		invalid_spectra = []
		for spectrum in spectra: 
			if not self.has_all_keys(spectrum): 
				print('MGFError: lacking necessary keys in mgf file, skip this spectrum')
				print('expected keys in mgf: (\'title\', \'{}\', \'precursor_type\', \'collision_energy\')'.format(self.precursor_mz_key))
				continue

			# filter out invalid data
			maxium_mz = np.max(spectrum['m/z array'])
			minium_mz = np.min(spectrum['m/z array'])
			if maxium_mz < general_filter_config['min_mz'] or maxium_mz > general_filter_config['max_mz'] or \
				len(spectrum['m/z array']) < general_filter_config['min_peak_num']: 
				invalid_spectra.append(spectrum)
			else: 
				clean_spectra.append(spectrum)
		return clean_spectra, invalid_spectra

	def has_all_keys(self, spec): 
		if self.use_simulated_precursor_mz:
			keys = ['title', 'simulated_precursor_mz', 'precursor_type', 'collision_energy']
		else:
			keys = ['title', 'precursor_mz', 'precursor_type', 'collision_energy']
		for k in keys:
			if k not in spec['params'].keys(): 
				return False
		return True
	
	def load_mgf_spectra(self, spectra, encoder):  
		for spectrum in spectra: 
			good_spec, _, _, spec_arr = generate_ms(x=spectrum['m/z array'], 
													y=spectrum['intensity array'], 
													precursor_mz=float(spectrum['params'][self.precursor_mz_key]), 
													resolution=encoder['resolution'], 
													max_mz=encoder['max_mz'], 
													charge=int(encoder['type2charge'][spectrum['params']['precursor_type']]))
			if not good_spec: 
				continue

			adjust_neutral_add_vec, adjust_precursor_type = self.melt_neutral_precursor(spectrum['params']['precursor_type'])
			
			ce, nce = parse_collision_energy(ce_str=spectrum['params']['collision_energy'], 
						precursor_mz=float(spectrum['params'][self.precursor_mz_key]), 
						charge=abs(int(encoder['type2charge'][spectrum['params']['precursor_type']])))
			if ce == None and nce == None: # can not process '30-50 eV'
				continue

			env_arr = np.array([float(spectrum['params'][self.precursor_mz_key]), 
								nce, 
								encoder['precursor_type'][adjust_precursor_type]]) 
			
			na_arr = np.array(adjust_neutral_add_vec)

			self.data.append({'title': spectrum['params']['title'], 'precursor_type': spectrum['params']['precursor_type'], 
								'spec': spec_arr, 'env': env_arr, 'neutral_add': na_arr})

	def melt_neutral_precursor(self, precursor_type): # Used for testing only 
		precursor_type = unify_precursor_type(precursor_type)

		neutrue_list = ['CH4O2', 'CH2O2', 'H2O', 'NH3', 'CO2']
		neutrue_counts = {}

		# Step 1: Get the count of neutral losses/adducts
		for neutrue in neutrue_list:
			if neutrue in precursor_type:
				pattern = r'([-+]?\d*)' + neutrue
				count = re.findall(pattern, precursor_type)
				if count: 
					count = count[0]
					if count == '+': count = 1
					elif count == '-': count = -1
					else: count = int(count)
					neutrue_counts[neutrue] = count
					break # only one neutral adduct is allowed

		# Step 2: Remove neutral losses/adducts from the precursor type string
		pattern = r'([-+]?\d*)(?:' + '|'.join(neutrue_list) + ')'
		adjust_precursor_type = re.sub(pattern, '', precursor_type)

		# Step 3: Convert the neutral losses/adducts into vector
		adjust_neutral_add = {}
		for neutrue, count in neutrue_counts.items(): 
			n_dict = formula_to_dict(neutrue)
			for k, v in n_dict.items(): 
				if k in adjust_neutral_add:
					adjust_neutral_add[k] += v * count
				else:
					adjust_neutral_add[k] = v * count
		adjust_neutral_add_vec = self.formula_dict_to_vector(adjust_neutral_add)
		
		return adjust_neutral_add_vec, adjust_precursor_type

	def formula_dict_to_vector(self, formula_dict): 
		vector = [0] * len(ATOMS_INDEX)

		for atom, count in formula_dict.items(): 
			index = ATOMS_INDEX.get(atom, None)
			if index is not None:
				vector[index] = int(count) if count else 1

		return vector
