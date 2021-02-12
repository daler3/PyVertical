class DataOwnerPsi:
    def __init__(self, name, data_dir=None, label_dir=None, index_dir=None):
        self.name = name
        
        #load data
        self.index_list = self.__load_data(index_dir) 
        data_list = self.__load_data(data_dir) 
        label_list = self.__load_data(label_dir) 
        
        #create dataset
        self.dataset = self.__create_dataset(data_list, label_list, self.index_list)
        
        self.duet = None
    
        
    def __load_data(self, directory):
        return pickle.load(open(directory, 'rb'), encoding='utf-8') if directory else None
    
    def __create_dataset(self, data_list, label_list, index_list):
        if not index_list: 
            label_set = torch.Tensor(label_list) if label_list else None
            bs = torch.Tensor(data_list) if data_list else None
            dataset = SampleSetWithLabelsNoIndex(label_set, bs) if (label_set and bs) else (label_set or bs)

        else: #there is index
            label_set = BaseIndexSet(index_list, label_list, is_labels=True) if label_list else None
            bs = BaseIndexSet(index_list, data_list, is_labels=False) if data_list else None
            dataset = SampleIndexSetWithLabels(label_set, bs) if (label_set and bs) else (label_set or bs)
            
        return dataset
        
    
    def connect_to_duet(self, loopback=True):
        self.duet = sy.launch_duet(loopback=loopback)
        return self.duet 
    
    def initiate_psi(self,psiProtocol):
        #if there are no indexes, we cannot start Psi
        if not self.index_list: 
            raise Exception("You cannot initiate PSI if your dataset does not have indexes") 
        
 
        self.protocol = psiProtocol(self.duet, self.dataset)    