from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib

SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg2://{user}:{pwd}@{ip}/{db_name}'.format(
    user= 'dlzdowvu',
    pwd=urllib.parse.quote('uJs3nB6PIBPq1p2iMtgbe8vRLeDHkjyj'),
    ip= 'satao.db.elephantsql.com',
    db_name='dlzdowvu'
    )
print(SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
