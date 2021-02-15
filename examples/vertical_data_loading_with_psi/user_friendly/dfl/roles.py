import datasets
from datasets import BaseIndexSet, SampleIndexSetWithLabels
import torch
import syft as sy
from abc import ABC, abstractmethod
import pickle
import psi_cls


class DuetRole(ABC): 
    def __init__(self, data_dir=None, label_dir=None, index_dir=None, name=""):
        
        self.name = name
        
        #load data
        self.index_list = self.__load_data(index_dir) 
        data_list = self.__load_data(data_dir) 
        label_list = self.__load_data(label_dir) 
        
        #create dataset
        self.dataset = self.__create_dataset(data_list, label_list, self.index_list)
        
        self.duet = None
        self.__protocol = None
        
    def __load_data(self, directory):
        return pickle.load(open(directory, 'rb'), encoding='utf-8') if directory else None
    
    def __create_dataset(self, data_list, label_list, index_list):
        if not index_list: 
            label_set = torch.Tensor(label_list) if label_list else None
            bs = torch.Tensor(data_list) if data_list else None
            dataset = SampleSetWithLabelsNoIndex(label_set, bs) if (label_set and bs) else (label_set or bs)

        else: #there is index
            label_set = BaseIndexSet(index_list, self.name, label_list, is_labels=True) if label_list else None
            bs = BaseIndexSet(index_list, self.name, data_list, is_labels=False) if data_list else None
            dataset = SampleIndexSetWithLabels(label_set, bs, self.name) if (label_set and bs) else (label_set or bs)
            
        return dataset
        
    @abstractmethod
    def connect_to_duet(self, loopback=True, server_id=None):
        pass
    
    @property
    def protocol(self):
        return self.__protocol
    
    @protocol.setter
    def protocol(self, psi_prot):
        assert type(psi_prot) == PsiProtocol, "The protocol should be a PSI Protocol"
        self.__protocol = psi_prot


class DataScientist(DuetRole):
    def __init__(self, *args, **kwargs): 
        super(DataScientist,self).__init__(*args, **kwargs)
        self.duet_list = []
        self.do_names = []
    
    def connect_to_duet(self, loopback=True, server_id=None, name=None):
        duet = sy.join_duet(loopback=loopback) if loopback else sy.join_duet(server_id)
        self.duet_list.append(duet)
        if name: 
            self.do_names.append(name)
        return duet

    @protocol.setter
    def protocol(self, psi_prot):
        assert type(psi_prot) == PsiProtocol, "The protocol should be a PSI Protocol"
        if type(psi_prot) == DSPsiStar:
            self.__protocol = psi_prot(self.duet_list)
        if type(psi_prot) == PsiProtocolDS:
            self.__protocol = psi_prot()

        
class DataOwner(DuetRole):    
    def connect_to_duet(self, loopback=True):
        self.duet = sy.launch_duet(loopback=loopback)
        return self.duet 
    
    @protocol.setter
    def protocol(self, psi_prot):
        assert type(psi_prot) == PsiProtocol, "The protocol should be a PSI Protocol"
        self.__protocol = psi_prot(self.duet, self.dataset)
