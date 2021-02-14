import syft as sy 
import openmined_psi as psi
import torch 
from abc import ABC

class PsiProtocolDO(ABC):
    def __init__(self, duet, dataset, fpr=1e-6, reveal_intersection=True):
        self.duet = duet
        self.dataset = dataset
        self.data_ids = list(map(str, list(map(int, dataset.ids))))
        self.fpr = fpr
        self.reveal_intersection = reveal_intersection
        super().__init__()
        
        self.__start_protocol()
        
        
    def __start_protocol(self):
        self.__one_to_one_exchange_init()
        
        
    def __one_to_one_exchange_init(self):
        self.__add_handler_accept(self.duet, tag="reveal intersection")
        self.__add_handler_accept(self.duet, tag="fpr")
        
        sy_reveal_intersection = sy.lib.python.Bool(self.reveal_intersection)
        sy_reveal_intersection_ptr = sy_reveal_intersection.tag("reveal_intersection").send(self.duet, searchable=True)
        
        sy_fpr = sy.lib.python.Float(self.fpr)
        sy_fpr_ptr = sy_fpr.tag("fpr").send(self.duet, searchable=True)
        
        
    def one_to_one_exchange_setup(self):
        client_items_len = self.__get_object_duet(tag="client_items_len")
        self.server = psi.server.CreateWithNewKey(reveal_intersection)
        setup = self.server.CreateSetupMessage(self.fpr, client_items_len, self.data_ids)
        self.__add_handler_accept(self.duet, tag="setup")
        setup_ptr = setup.send(self.duet, searchable=True, tags=["setup"], description="psi.server Setup Message")
        
        
    def one_to_one_exchange_reply(self):
        request_ptr = self.__get_object_duet(tag="request")
        response = server.ProcessRequest(request) 
        self.__add_handler_accept(duet, tag="response")
        response_ptr = response.send(duet, searchable=True, tags=["response"], description="psi.server response")      
        
        
    def __get_object_duet(self, tag=""):
        return duet.store[tag].get(delete_obj=False)
    
    
    def __add_handler_accept(self, duet, action="accept", tag=""):
        duet.requests.add_handler(
                tags=[tag],
                action="accept"
        )

class PsiOneToOne(PsiProtocolDO): 
    def __start_protocol(self):
        super.__start_protocol(self)

        
class PsiStar(PsiProtocolDO):
    def __start_protocol(self):
        super.__start_protocol(self)
        
    def retrieve_intersection():
        id_int = self.__get_object_duet(tag="ids_intersec")
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
        label_tensor = torch.Tensor(label_list_toshare)
        id_tensor = torch.Tensor(id_list_toshare)

        return value_tensor, label_tensor, id_tensor