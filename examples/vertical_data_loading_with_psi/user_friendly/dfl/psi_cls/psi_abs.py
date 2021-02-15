from psi_status_tag import PSI_STATUS
from abc import ABC, abstractmethod

class PsiProtocol(ABC):
    def __init__(self, duet):
        self.duet = duet
        self.__status = PSI_STATUS.PRE
    
    @abstractmethod
    def psi_setup(self):
        pass
    
    @abstractmethod
    def psi_response(self):
        pass
    
    @abstractmethod
    def __get_object_duet(self, tag=""):
        pass
    
    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, status):
        assert type(status) == PSI_STATUS, "The statis should be a valid PSI Status"
        self.__status = status