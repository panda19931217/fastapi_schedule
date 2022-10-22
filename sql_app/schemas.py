from typing import List, Union

from pydantic import BaseModel


class ScheduleBase(BaseModel):
    month: int
    date: list

class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
#===========================

class LeaveBase(BaseModel):
    month: int
    date: list
    period: str

class LeaveCreate(LeaveBase):
    pass

class Leave(LeaveBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
#===========================

class UserBase(BaseModel):
    email: str
    user_name:str
    memmber_type:str='Staff'
    skill:str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    schedule: List[Schedule] = []
    leave: List[Leave] = []

    class Config:
        orm_mode = True
