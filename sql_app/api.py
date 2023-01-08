from typing import List, Union
from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from . import crud, models, schemas
from .database import SessionLocal, engine
import uvicorn
import calendar
from .schedule import ortools_sechedule

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000"
]


# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =======OAuth2 with Password (and hashing), Bearer with JWT tokens======================
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    plain_hashed_password = plain_password + "notreallyhashed"
    # return pwd_context.verify(plain_hashed_password, hashed_password)
    return plain_hashed_password == hashed_password


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(user_name: str, password: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_name(db, user_name=user_name)

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_name(db, user_name=token_data.username)

    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: schemas.User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.user_name}]


# =================================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


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
def read_user_by_id(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/schedule")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    lst_info = []
    for num, info in enumerate(users):
        if not info.schedule:
            continue
        for schedule in info.schedule:
            dic_info = {
                'user_name': info.user_name,
                'year': schedule.year,
                'month': schedule.month,
                'date': schedule.date,
                'period': schedule.period,
                'user_num': num
            }
            lst_info.append(dic_info)
    return lst_info


@app.post("/users/{user_id}/schedule/", response_model=schemas.Schedule)
def create_schedule_for_user(
        user_id: int, schedule: schemas.ScheduleCreate, db: Session = Depends(get_db)
):
    return crud.create_user_schedule(db=db, schedule=schedule, user_id=user_id)


# @app.get("/schedule/", response_model=List[schemas.Schedule])
# def read_schedule(int_month: int = 1, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     schedule = crud.get_schedule(db, int_month=int_month, skip=skip, limit=limit)
#     return schedule


@app.post("/users/{user_id}/leave/", response_model=schemas.Leave)
def create_leave_for_user(
        user_id: int, leave: schemas.LeaveCreate, db: Session = Depends(get_db)
):
    return crud.create_user_leave(db=db, leave=leave, user_id=user_id, year=leave.year, month=leave.month)

@app.get("/leave")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    lst_info = []
    for num, info in enumerate(users):
        if not info.leave:
            continue
        for leave in info.leave:
            dic_info = {
                'user_name': info.user_name,
                'year': leave.year,
                'month': leave.month,
                'date': leave.date,
                'period': leave.period,
                'user_num': num
            }
            lst_info.append(dic_info)
    return lst_info


# @app.get("/leave/", response_model=List[schemas.Schedule])
# def read_leave(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     leave = crud.get_leave(db, skip=skip, limit=limit)
#     return leave

@app.get("/calculate/schedule_and_leave")
def calculate_schedule_and_leave(year: int = 2023, month: int = 1, db: Session = Depends(get_db)):
    day_of_this_month = calendar.monthrange(year, month)[1]
    leave = crud.get_leave_by_month(db, month=month)
    lst_employees = []
    lst_leave = []
    for info in leave:
        for date in info.date.split(','):
            lst_employees.append(str(info.owner_id)) if str(info.owner_id) not in lst_employees else lst_employees
            if date == '0':
                continue
            lst_in = [str(info.owner_id), int(date)]
            lst_leave.append(lst_in)

    output = ortools_sechedule(
        lst_employees=['4', '5', '6', '7'],
        day_of_this_month=day_of_this_month,
        max_employee_one_shifts=3,
        min_employee_one_shifts=2,
        max_continue_shifts=5,
        lst_leave=[]
    )
    print(output)
    for i in output:
        print(list(i.values())[0])
        dic_schedule = {
            "month": month,
            "date": ','.join(map(str, list(i.values())[0]))
        }
        crud.create_user_schedule(db=db, schedule=schemas.ScheduleBase(**dic_schedule), user_id=int(list(i.keys())[0]),
                                  year=year, month=month)
