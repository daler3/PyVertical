#imports
import syft as sy 
import openmined_psi as psi
import torch 
from abc import ABC

class DSPsiProtocolSingle:
    
    def __init__(self, duet, index_subset):
        self.duet = duet
        self.index_subset = index_subset
    
    def psi_init(self):
        reveal_intersection_ptr = self.__get_object_duet(tag="reveal_intersection")
        reveal_intersection_ptr.request(reason="I want to know if I need to reveal intersection",timeout_secs=-1)
        self.reveal_intersection = reveal_intersection_ptr.get()
        
        fpr_ptr = self.__get_object_duet(tag="fpr")
        fpr_ptr.request(reason="I want to know the fpr", timeout_secs = -1)
        fpr = fpr_ptr.get()
        
        sy_client_items_len = sy.lib.python.Int(len(self.index_subset))
        sy_client_items_len_ptr = sy_client_items_len.send(duet, searchable=True, tags=["client_items_len"], description="client items length")
    
    def psi_setup(self):
        #wait for 
        setup_ptr = self.__get_object_duet(tag="setup")
        setup_ptr.request(reason="I want to get the PSI setup", timeout_secs = -1)
        self.setup = setup_ptr.get()
        
        #create client request
        client = psi.client.CreateWithNewKey(self.reveal_intersection)
        request = client.CreateRequest(self.index_subset)
        
        #request
        request_ptr = request_1.send(self.duet, tags=["request"], searchable=True, description="client request")
        
        
    def psi_response(self):
        response_ptr = self.__get_object_duet(tag="response")
        response_ptr.request(reason="I want to get the PSI setup", timeout_secs = -1)
        response = response_ptr.get()
        
        if self.reveal_intersection:
            intersection = client.GetIntersection(setup, response)
            iset = set(intersection)
            
        return intersection
    
    
    def __get_object_duet(self, tag=""):
        return self.duet.store[tag].get(delete_obj=False)


class Protocol_DS_coordinate():

	def __init__(self, duet_list, index_subset):
		assert len(duet_list) > 0,  "At least one duet reference should be provided"
		self.duet_list = duet_list
		self.index_subset = index_subset

		self.protocol_list = []
		for duet_instance in self.duet_list: 
			self.protocol_list.append(DSPsiProtocolSingle(duet_instance, index_subset))


	def global_init(self):
		for protocol in self.protocol_list:
			protocol.psi_init()

	def global_setup(self):
		for protocol in self.protocol_list:
			protocol.psi_setup()

	def global_response(self):
		intersection_list = []
		for protocol in self.protocol_list:
			intersection_list.append(psi_response())

		self.__global_intersection(intersection_list)


	def __global_intersection(self, intersection_list):
		intersection_sets = map(set, intersection_list)
		global_int = torch.Tensor(list(set.intersection(*intersection_sets)))
		#I get the id that I have, I reshare now
		for duet_instance in self.duet_list:
			global_int.send(duet_instance, tags=["ids_intersec"], searchable=True, description="intersection ids")
		