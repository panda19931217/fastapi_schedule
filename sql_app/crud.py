from sqlalchemy.orm import Session

import models, schemas

from datetime import datetime

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    present_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password,create_time=present_time,user_name=user.user_name,memmber_type=user.memmber_type,skill=user.skill)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_schedule(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Schedule).offset(skip).limit(limit).all()


def create_user_schedule(db: Session, schedule: schemas.ScheduleCreate, user_id: int):
    db_schedule = models.Schedule(**schedule.dict(), owner_id=user_id)
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def get_leave(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Leave).offset(skip).limit(limit).all()


def create_user_leave(db: Session, leave: schemas.ScheduleCreate, user_id: int):
    db_leave = models.Leave(**leave.dict(), owner_id=user_id)
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave

