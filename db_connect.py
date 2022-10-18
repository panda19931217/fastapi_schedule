import pandas as pd  

import glob

from sqlalchemy import create_engine, MetaData
import psycopg2
import io
import sys
import urllib

from cred_confs import ip, user, pwd, db_name
    
def create_and_write_to_table(df, table_name, method):
    sql_connection_string = 'postgresql+psycopg2://{user}:{pwd}@{ip}/{db_name}'.format(user=user,
                                                                                       pwd=urllib.parse.quote(pwd),
                                                                                       ip=ip,
                                                                                       db_name=db_name)
    engine = create_engine(sql_connection_string)
    
    df.head(0).to_sql(table_name, engine, if_exists=method,index=False) #truncates the table
    conn = engine.raw_connection()
    cur = conn.cursor()
    output = io.StringIO()
    df.to_csv(output, sep='|', header=False, index=False)
    output.seek(0)
    contents = output.getvalue()
    cur.copy_from(output, table_name, sep='|', null="") # null values become ''
    conn.commit()

def load_data_from_db(table_name):
    '''
    自DB讀取資料
    :param db_name: 資料庫名稱
    :param table_name: 資料表名稱
    :return: pd.dataframe
    '''
    sql_connection_string = 'postgresql+psycopg2://{user}:{pwd}@{ip}/{db_name}'.format(user=user,
                                                                                       pwd=urllib.parse.quote(pwd),
                                                                                       ip=ip,
                                                                                       db_name=db_name)
    engine = create_engine(str_conn)
    try:
        data = pd.read_sql_table( table_name , engine )
        return data
    except:
        print(f'{db_name}.{table_name} load data error.')
        return False
