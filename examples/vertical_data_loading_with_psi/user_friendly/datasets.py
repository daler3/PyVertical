import torch
from torch.utils.data import Dataset


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


class VerticalFederatedDataset():
    """
    VerticalFederatedDataset, which acts as a dictionary between BaseVerticalDatasets, 
    already sent to remote workers, and the corresponding workers.
    This serves as an input to VerticalFederatedDataLoader. 
    Same principle as in Syft 2.0 for FederatedDataset: 
    https://github.com/OpenMined/PySyft/blob/syft_0.2.x/syft/frameworks/torch/fl/dataset.py
    
    Args: 
        datasets: list of BaseVerticalDatasets.
    """
    def __init__(self, datasets, n_samples=50):
        
        self.n_samples = n_samples
        
        self.datasets = {} #dictionary to keep track of BaseVerticalDatasets and corresponding workers
        
        #just assuming it is the same id list for now
        indices_list = datasets[0].ids
        
        #take intersecting items
        i = 0
        for dataset in datasets:
            self.datasets[i] = dataset
            i+=1
        
        #create a list of dictionaries
        self.dict_items_list = []
 
        #assuming it is sequential now, we need PSI for making this properly
        for index in range(0, n_samples):
            curr_dict = {}
            for w in range(0,i):
                curr_dict[w] = self.datasets[w][index]
            self.dict_items_list.append(curr_dict)
            if index % 10 == 0:
                print(index)
            
        #self.indices = list(indices_list)
            

    def __getitem__(self, idx):
        """
        Args:
            worker_id[str,int]: ID of respective worker
        Returns:
            Get dataset item from different workers
        """

        return self.dict_items_list[idx]

    def __len__(self):
        #return len(self.indices)
        return self.n_samples

    def __repr__(self):

        fmt_str = "FederatedDataset\n"
        #fmt_str += f"    Distributed accross: {', '.join(str(x) for x in self.datasets.keys())}\n"
        #fmt_str += f"    Number of datapoints: {self.__len__()}\n"
        return fmt_str
    
    def collate_fn(self, batch):
        return batch[0]
