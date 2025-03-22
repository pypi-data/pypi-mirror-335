from typing import TypeVar, Generic, get_origin
from pydantic import BaseModel


T = TypeVar('T')

class IntResult(BaseModel):
    result: int
class FloatResult(BaseModel):
    result: float
class BoolResult(BaseModel):
    result: bool
class ListResult(BaseModel, Generic[T]):
    result: list[T]

t = list[int]
print(isinstance(ListResult, Generic))
print(get_origin(int))
print(t)  # typing.List[int]

print(get_origin(t) is list)  # True - this is the correct way to check

print(isinstance(t, list))
print(isinstance(t, Generic))

subtype = t.__args__[0]

print(subtype)

lr = ListResult[subtype]

print(lr)

