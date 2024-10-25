import sqlite3
import pandas as pd
import os
import sys
def resource_path(relative_path):
    """ Get absolute path to resource, works for both dev and PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # If not running as a PyInstaller bundle, use the current directory
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

database = resource_path('app_data/MainDataBase.db')  # database file address
default_table = 'None'

# MASTER ========================================================================
def get_all_tables():
    try:
        query = '''
        SELECT name 
        FROM sqlite_master 
        WHERE type = 'table';
        '''
        return execute_command(query, selection=True)
    except Exception as e: print(f'Error in get_all_tables: {e}')
# CONN & EXECUTE ================================================================
def make_connection(db_file=database):
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e: print(f'Error in make_connection: {e}')
def execute_command(query:str,values:tuple=(),selection:bool=False):
    try:
        conn, cursor = make_connection()
        cursor.execute(query, values)
        conn.commit()
        if selection:
            return cursor.fetchall()
    except Exception as e: print(f'Error in execute_command: {e}')

# TABLE =========================================================================
def create_table(table_name:str=default_table,columns:dict={},set_as_default:bool=False):
    try:
        query = f'''create table {table_name} ({','.join(map(lambda x: x + ' ' + columns[x], columns.keys()))})'''
        execute_command(query)
        if set_as_default:
            global default_table
            default_table = table_name
    except Exception as e: print(f'Error in creat_table: {e}')

def get_table_columns(table_name:str=default_table,name_only:bool=False):
    try :
        query = f'''
            PRAGMA table_info({table_name});
        '''
        data = execute_command(query, selection=True)
        if name_only:
            return list(map(lambda x: x[1], data))
        else:
            return data
    except Exception as e: print(f'Error in get_table_columns: {e}')

def add_to_table(table_name:str=default_table,values:dict={}):
    try:
        query = f'''
        INSERT INTO {table_name}({','.join(values.keys())})
        values({','.join('?' * len(values))})
        '''
        execute_command(query, tuple(values.values()))
    except Exception as e: print(f'Error in add_to_table: {e}')

def get_table_data(table_name:str=default_table,selections:tuple='*',condition:str='',condition_values:tuple=(),
                   limit:int=-1,as_dataframe:bool=False):
    try:
        # selections
        if selections == '*':
            pass
        else:
            selections = ','.join(selections)

        if limit > 0:
            limit = 'limit ' + str(limit)
        else:
            limit = ''
        # conditions
        if condition:
            query = f"SELECT {selections} FROM {table_name} WHERE {condition} " + limit
            values = condition_values
        else:
            query = f"SELECT {selections} FROM {table_name}" + limit
            values = ()
        table_data=execute_command(query,values=values,selection=True)

        # as df
        if as_dataframe:
            if selections  == '*':
                headers = get_table_columns(table_name,name_only=True)
            else:
                headers = selections.split(',')
            dataframe = pd.DataFrame(columns=headers,data=table_data)
            result= dataframe
        else:
            result= table_data
        return result
    except Exception as e: print(f'Error in get_table_data : {e}')


def to_df(headers,rows):
    try:
        data_frame = pd.DataFrame(data=rows, columns=headers)
        return data_frame
    except Exception as e: print(f'Error in to_df: {e}')

# clearing ----------------------------------------------
def clear_table(table_name:str=default_table):
    try :
        query = f'''
            delete from {table_name}
            '''
        execute_command(query,)
    except Exception as e: print(f'error in clear_table : {e}')

def update_table(table_name:str=default_table,set:dict={},conditions:str='',condition_values:tuple=()):
    try :
        sets = list(map(lambda x, y: f'{x} = {y}', set.keys(), set.values()))
        sets = ','.join(sets)
        query = f'''
            UPDATE {table_name} set {'= ?,'.join(set.keys())+' = ?'} 
            where {conditions}
        '''
        values = tuple(set.values())+condition_values
        execute_command(query,values)
    except Exception as e: print(f'error in update_table : {e}')
def delete_table_row(table_name:str=default_table,conditions:str='',condition_values:tuple=()):
    try:
        query = f'''
            DELETE FROM {table_name}
            where {conditions}
        '''
        values = condition_values
        execute_command(query, values)
    except Exception as e: print(f'error in delete_table_row : {e}')

if __name__ == '__main__':
    # create_table('Users',
    #              {'id':'integer primary key','name':'CHAR','password':'CHAR'}
    #              ,set_as_default=True)
    # create_table('Passwords',
    #              {'id': 'integer primary key', 'user_id': 'INTEGER',
    #                     'app_name':'CHAR','app_username':'CHAR', 'app_password': 'BLOB','password_key':'BLOB','app_description':'CHAR'})
    # create_table('Logs',
    #              {'id': 'integer primary key', 'user_id': 'INTEGER','device_id': 'CHAR'})
    # clear_table('Users')
    # clear_table('Passwords')
    # clear_table('Logs')
    # update_table('Passwords',set={'app_name':'123','app_description':'3'},conditions='user_id=1')
    pass
