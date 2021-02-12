class PsiProtocol(ABC):
    def __init__(self, duet, dataset, fpr=1e-6):
        self.duet = duet
        self.dataset = dataset
        self.data_ids = list(map(str, list(map(int, dataset.ids))))
        self.fpr = fpr
        super().__init__()
        
        self._start_protocol()
    
    @abstractmethod
    def __start_protocol(self):
        self._one_to_one_exchange()
            
    def __one_to_one_exchange(self):
        self._add_handler(self.duet, name="reveal intersection")
        self._add_handler(self.duet, name="fpr")
        
        reveal_intersection = True
        sy_reveal_intersection = sy.lib.python.Bool(reveal_intersection)
        sy_reveal_intersection_ptr = sy_reveal_intersection.tag("reveal_intersection").send(self.duet, searchable=True)
        
        sy_fpr = sy.lib.python.Float(self.fpr)
        sy_fpr_ptr = sy_fpr.tag("fpr").send(self.duet, searchable=True)
        
        #client items len
        client_items_len = self.__get_object_duet(tag="client_items_len")
        
        #server
        self.server = psi.server.CreateWithNewKey(reveal_intersection)
        setup = self.server.CreateSetupMessage(self.fpr, client_items_len, self.data_ids)
        
        self.__add_handler_accept(self.duet, name="setup")
        
        setup_ptr = setup.send(self.duet, searchable=True, tags=["setup"], description="psi.server Setup Message")
        
        #get the request
        request_ptr = self.__get_object_duet(tag="request")
        
        #response
        response = server.ProcessRequest(request)
        
        self.__add_handler_accept(duet, name="response")
        
        response_ptr = response.send(duet, searchable=True, tags=["response"], description="psi.server response")
        
    def __one_to_one_exchange_client(self):
        pass
        
    def __add_handler_accept(self, duet, action="accept", name=""):
        duet.requests.add_handler(
                name=name,
                action="accept"
        )
        
        
    def __get_object_duet(self, tag=""):
        
        while True: 
            try:
                self.duet.store[tag]
            except:
                continue
            break

        return duet.store[tag].get(delete_obj=False)
    
    
    def __get_ids_and_share(self):
        #let's get Data Scientist's ids for global intersection
        id_int = self._get_object_duet(tag="ids_intersec")
        
        #map the ids to a list of integers
        id_int_list = list(map(int, list(id_int)))
        
        #convert the values to share in tensors
        value_tensor, label_tensor, id_tensor = self.__convert_values_toshare(id_int_list)
        
        #share those values
        value_tensor_ptr = value_tensor.send(self.duet, searchable=True, tags=["values"], description="intersecting values")
        label_tensor_ptr = label_tensor.send(self.duet, searchable=True, tags=["labels"], description="intersecting labels")
        id_tensor_ptr = id_tensor.send(self.duet, searchable=True, tags=["ids"], description="intersecting ids")
        
    
    def __convert_values_toshare(self, id_int_list):
        value_list_toshare = []
        label_list_toshare = []
        id_list_toshare = []
        for k in self.dataset.values_dic.keys():
            if int(k) in id_int_list:
                tuple_ = self.dataset.values_dic[k]
                value_list_toshare.append(tuple_[0])
                label_list_toshare.append(tuple_[1])
                id_list_toshare.append(int(k))

        value_tensor = torch.cat(value_list_toshare)




class PsiOneToOne(PsiProtocol): 
    def __start_protocol(self):
        super.__start_protocol(self)

        
class PsiStar(PsiProtocol):
    def __start_protocol(self):
        super.__start_protocol(self)
        
        super.__get_ids_and_share()
        label_tensor = torch.Tensor(label_list_toshare)
        id_tensor = torch.Tensor(id_list_toshare)

        return value_tensor, label_tensor, id_tensor
