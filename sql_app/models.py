from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    skill = Column(String, index=True)
    memmber_type = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    create_time = Column(String, index=True)

    Schedule = relationship("Schedule", back_populates="owner")
    Leave = relationship("Leave", back_populates="owner")


class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer, index=True)
    date = Column(Integer, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="Schedule")

class Leave(Base):
    __tablename__ = "leave"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer, index=True)
    date = Column(Integer, index=True)
    period = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="Leave")
