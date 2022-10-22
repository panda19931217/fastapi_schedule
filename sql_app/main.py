from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine
import uvicorn 

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/schedule/", response_model=schemas.Schedule)
def create_schedule_for_user(
    user_id: int, schedule: schemas.ScheduleCreate, db: Session = Depends(get_db)
):
    return crud.create_user_schedule(db=db, schedule=schedule, user_id=user_id)


@app.get("/schedule/", response_model=List[schemas.Schedule])
def read_schedule(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    schedule = crud.get_schedule(db, skip=skip, limit=limit)
    return schedule


@app.post("/users/{user_id}/leave/", response_model=schemas.Leave)
def create_leave_for_user(
    user_id: int, leave: schemas.LeaveCreate, db: Session = Depends(get_db)
):
    return crud.create_user_leave(db=db, leave=leave, user_id=user_id)


@app.get("/leave/", response_model=List[schemas.Schedule])
def read_leave(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    leave = crud.get_leave(db, skip=skip, limit=limit)
    return leave


if __name__ == "__main__":
    uvicorn.run(
            app="main:app")