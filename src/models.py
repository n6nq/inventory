# this file defines all the models used in the inventory program.  
# Each model is a subclass of BaseModel, which is a subclass of pydantic.BaseModel.  
# Each model also implements the ListMember interface, which defines methods for displaying 
# the model as a string and searching for a string within the model.

from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Protocol, runtime_checkable

@runtime_checkable
class ListMemberProtocol(Protocol):
    
    @property
    def id(self) -> int:
        ...

    def str_all(self) -> str:
        ...

    def str_name(self) -> str:
        ...

    def has_str(self, astr: str) -> bool:
        ...

class ListMember(BaseModel, ABC):
    id: int

    @abstractmethod
    def str_all(self) -> str:
        ...
    @abstractmethod
    def str_name(self) -> str:
        ...
    @abstractmethod
    def has_str(self, astr: str) -> bool:
        ...
        
class Item(ListMember):
    id: int
    cat_id: int
    cat_str: str
    type_id: int
    type_str: str
    sub_id: int
    sub_str: str
    box: str
    loc: str
    descript: str

    @classmethod
    def from_empty(cls):
        return cls(id=0, cat_id=0, cat_str='', type_id=0, type_str='', sub_id=0, sub_str='', box='', loc='', descript='')

    def has_str(self, astr: str) -> bool:
        if astr in self.cat_str or astr in self.type_str or astr in self.sub_str or astr in self.box or astr in self.loc or astr in self.descript:
            return True
        return False

    def str_all(self) -> str:
        if self.id == 0:
            return 'Empty'       # this how to display an uninitialized Item

        return str(self.id)+', '+self.cat_str+', '+self.type_str+', '+self.sub_str+', '+self.box+', '+self.loc+', '+self.descript

    def str_name(self) -> str:
        return self.str_all()


class Category(ListMember):
    id: int
    c_name: str

    def has_str(self, astr: str) -> bool:
        if astr in self.c_name:
            return True
        return False

    def str_all(self) -> str:
        return str(self.id)+', '+self.c_name

    def str_name(self) -> str:
        return self.c_name

class Type(ListMember):
    id: int
    t_name: str
    cat_id: int

    def has_str(self, astr: str) -> bool:
        if astr in self.t_name:
            return True
        return False

    def str_all(self) -> str:
        return str(self.id)+', '+self.t_name+', '+str(self.cat_id)

    def str_name(self) -> str:
        return self.t_name


class Subtype(ListMember): 
    id: int
    st_name: str
    atype: int

    def has_str(self, astr: str) -> bool:
        if astr in self.st_name:
            return True
        return False

    def str_all(self) -> str:
        return str(self.id)+', '+self.st_name+', '+str(self.atype)

    def str_name(self) -> str:
        return self.st_name


class String(ListMember):
    id: int = 0
    string: str

    def has_str(self, astr: str) -> bool:
        if astr in self.string:
            return True
        return False

    def get_str(self, index: int) -> str:
        return self.string[index:]

    def str_all(self) -> str:
        return self.string

    def str_name(self) -> str:
        return self.string
