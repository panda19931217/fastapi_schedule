from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib
from cred_confs import ip, user, pwd, db_name

SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg2://{user}:{pwd}@{ip}/{db_name}'.format(
    user=user,
    pwd=urllib.parse.quote(pwd),
    ip=ip,
    db_name=db_name
    )

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
