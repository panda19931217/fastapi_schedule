from typing import List, Union

from pydantic import BaseModel


class ScheduleBase(BaseModel):
    year: int
    month: int
    date: int
    period: str


class ScheduleCreate(ScheduleBase):
    pass


class Schedule(ScheduleBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
# ===========================


class LeaveBase(BaseModel):
    year: int
    month: int
    date: int
    period: str


class LeaveCreate(LeaveBase):
    pass


class Leave(LeaveBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


# ===========================


class UserBase(BaseModel):
    email: str
    user_name: str
    resturant_nb: int
    memmber_type: str = 'Staff'
    skill: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    schedule: List[Schedule] = []
    leave: List[Leave] = []

    class Config:
        orm_mode = True
