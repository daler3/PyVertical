#imports
import syft as sy 
import openmined_psi as psi
import pickle
import torch 
from torch.utils.data import Dataset
from abc import ABC, abstractmethod
import openmined_psi as psi


class SampleSetWithLabelsNoIndex(Dataset):
    def __init__(self, labelset, sampleset):
        self.labelset = labelset
        self.sampleset = sampleset 
        
    def __getitem__(self, index):
        """
        Args: 
            idx: index of the example we want to get 
        Returns: a tuple with data, label, index of a single example.
        """
        return tuple([self.sampleset[index], self.labelset[index]])
    
    def __len__(self):
        """
        Returns: amount of samples in the dataset
        """
        return self.values.shape[0]
    
    

class BaseIndexSet(Dataset):
    def __init__(self, ids, values, is_labels=False):
        self.values_dic = {}
        for i, l in zip(ids, values):
            self.values_dic[i] = l
        self.is_labels = is_labels

        self.ids = ids
        self.values = torch.Tensor(values) if is_labels else torch.stack(values)
    
    def __getitem__(self, index):
        """
        Args:
            idx: index of the example we want to get 
        Returns: a tuple with data, label, index of a single example.
        """
        return tuple([self.values[index], self.ids[index]])
    
    def __len__(self):
        """
        Returns: amount of samples in the dataset
        """
        return self.values.shape[0]

    
class SampleIndexSetWithLabels(Dataset):
    def __init__(self, labelset, sampleset):
        self.labelset = labelset
        self.sampleset = sampleset 
        
        self.labels = labelset.values
        self.values = sampleset.values
        self.ids = sampleset.ids
        
        self.values_dic = {}
        for k in labelset.values_dic.keys():
            self.values_dic[k] = tuple([sampleset.values_dic[k], labelset.values_dic[k]])
                                       
    def __getitem__(self, index):
        """
        Args: 
            idx: index of the example we want to get 
        Returns: a tuple with data, label, index of a single example.
        """
        return tuple([self.values[index], self.labels[index], self.ids[index]])
    
    def __len__(self):
        """
        Returns: amount of samples in the dataset
        """
        return self.values.shape[0]