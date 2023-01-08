from sqlalchemy.orm import Session

from . import models, schemas

from datetime import datetime


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_name(db: Session, user_name: str):
    return db.query(models.User).filter(models.User.user_name == user_name).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    present_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    user_dict = user.dict()
    user_dict.pop("password")
    db_user = models.User(hashed_password=fake_hashed_password,
                          create_time=present_time, **user_dict)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_schedule(db: Session, int_month: int = datetime.now().month, skip: int = 0, limit: int = 100):
    lst_dic_data = db.query(models.Schedule).filter(models.Schedule.month == int_month).offset(skip).limit(limit).all()
    return lst_dic_data


def create_user_schedule(db: Session, schedule: schemas.ScheduleCreate, user_id: int, year: int, month: int):
    db_schedule = models.Schedule(**schedule.dict(), owner_id=user_id)
    try:
        db.query(models.Schedule).filter(
            models.Schedule.owner_id == user_id,
            models.Schedule.year == year,
            models.Schedule.month == month,
        ).delete()
    except:
        pass
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def get_leave(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Leave).offset(skip).limit(limit).all()


def get_leave_by_month(db: Session, month: int):
    return db.query(models.Leave).filter(models.Leave.month == month).all()


def create_user_leave(db: Session, leave: schemas.ScheduleCreate, user_id: int, year: int, month: int):
    db_leave = models.Leave(**leave.dict(), owner_id=user_id)
    # try:
    db.query(models.Leave).filter(
        models.Leave.owner_id == user_id,
        models.Leave.year == year,
        models.Leave.month == month,
    ).delete()
    # except:
    #     pass
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave
