"""
This Python script uses the CSVs at 
https://github.com/chadwickbureau/baseballdatabank/tree/master/core.

It creates a MySQL database with pk-fk relationships.
A small amount of data is lost.

It first:
    * Creates lahmansbaseballdb MySQL database
    * Creates and populates leagues table
    * Creates and populates divisions table

    Note that the leagues and divisions tables are not included in the
    original Lahman data.

It then creates and populates these tables from CSVs in csvs folder
    in this order:
    1. teamsfranchises
    2. teams
    3. teamshalf
    4. people
    5. allstarfull
    6. appearances
    7. awardsmanagers
    8. awardsplayers
    9. awardssharemanagers
    10. awardsshareplayers
    11. batting
    12. battingpost
    13. schools
    14. collegeplaying
    15. fielding
    16. fieldingof
    17. fieldingofsplit
    18. fieldingpost
    19. halloffame
    20. parks
    21. homegames
    22. managers
    23. managershalf
    24. pitching
    25. pitchingpost
    26. salaries
    27. seriespost

    The order is important to maintain PK-FK relationships
"""
import os
import numpy as np
import pandas as pd
from subprocess import Popen, PIPE
import mysql.connector
import time

# Change to your login info
user = 'root'
password = '3C0ll@ge'

db_create_script = 'create-lahman-mysql.sql'

def file_path(relative_path):
    folder = os.path.dirname(os.path.abspath(__file__))
    path_parts = relative_path.split("/")
    new_path = os.path.join(folder, *path_parts)
    return new_path

def clear_log():
    open(file_path('log.txt'), 'w').close()

def log(msg):
    with open(file_path('log.txt'), 'a') as f:
        f.write(msg + '\n')

def db_connect():
    connection = mysql.connector.connect(
        host='127.0.0.1',
        user=user,
        password=password
    )

    return connection

def create_db(cursor):
    script = file_path(db_create_script)
    with open(script, encoding="utf-8") as f:
        commands = f.read().split(';')

    for command in commands:
        cursor.execute(command)

def get_tables():
    """
        returns the names of the CSV files in the order in which the
        tables are created in the database. The order is important
        to avoid key errors on inserts.
    """
    with open('create-lahman-mysql.sql') as f:
        lines = f.read().splitlines()

    starting_line = lines.index('/* LAHMAN TABLES */')
    lines = lines[starting_line:]

    start = len('CREATE TABLE ')
    tables = [
        line[start:].split(' ')[0]
        for line in lines
        if line.startswith('CREATE TABLE')
    ]

    return tables

def fix_value(value, col):
    # Return None for empty strings
    if isinstance(value, str) and len(value) == 0:
        return None

    # In most cases, NA stands for Not Applicable (I think)
    #   But, NA = 'National Association' for lgID
    if value == 'NA' and col != 'lgID':
        return None
    elif value=='MLN' and col=='teamID': # See *MLN in ReadMe file
        return 'ML1'
    elif value=='WSN' and col=='teamID': # See *WSN in ReadMe file
        return 'WAS'
    elif value=='inf':
        return None # Infinite ERAs
    
    return value

def get_columns(csv_cols, table):
    cols = []
    for col in csv_cols:
        col = col.replace('.','') # For Parks.csv and HomeGames.csv
        if col.lower() == 'rank':
            cols.append('teamRank')
        else:
            cols.append(col)
        
        if col in ['teamID', 'teamkey'] and table != 'teams':
            cols.append('team_ID')
        elif col == 'parkkey' and table != 'parks':
            cols.append('park_ID')
        elif col == 'divID':
            cols.append('div_ID')

    return cols

def get_values(orig_values, csv_cols, table, connection):
    values = []

    if table == 'allstarfull':
        year_id = orig_values[list(csv_cols).index('yearID')]
        team_id = orig_values[list(csv_cols).index('teamID')]

        try:
            if 1970 <= int(year_id) <= 1997 and team_id == 'MIL':
                orig_values[list(csv_cols).index('teamID')] = 'ML4' # See ReadMe
            if 1997 <= int(year_id) <= 2004 and team_id == 'LAA':
                orig_values[list(csv_cols).index('teamID')] = 'ANA' # See ReadMe
        except Exception as e:
            print(e, orig_values, csv_cols, table)
            print('Continue executing, but maybe should not.')

    for i in range(len(orig_values)):
        val = orig_values[i]
        col = csv_cols[i]
        col = col.replace('.','') # For Parks.csv and HomeGames.csv
        values.append(fix_value(val, col))

        # Add additional FK values
        fk = False
        if col in ['teamID', 'teamkey'] and len(val) and table != 'teams':
            if not len(val): # If col exists, but is empty
                values.append(None)
            else:
                query = '''SELECT ID FROM teams 
                           WHERE teamID = %s AND yearID = %s AND lgID = %s;'''
                try:
                    try:
                        year_id = orig_values[list(csv_cols).index('yearID')]
                    except ValueError: # yearID not in csv_cols
                        year_id = orig_values[list(csv_cols).index('year.key')]

                    try:
                        lg_id = orig_values[list(csv_cols).index('lgID')]
                    except ValueError: # lgID not in csv_cols
                        lg_id = orig_values[list(csv_cols).index('league.key')]
                except:
                    print(query, list(csv_cols), csv_cols, orig_values, sep='\n', end='\n\--------------n')
                    raise
                val = 'ML1' if val == 'MLN' else val # See *MLN in Readme file
                val = 'WAS' if val == 'WSN' else val # See *WSN in Readme file
                val = 'ML4' if (val == "MIL" and (1970 <= int(year_id) <= 1997)) else val
                val = 'ANA' if (val == "LAA" and (1997 <= int(year_id) <= 2004)) else val
                vals = [val, year_id, lg_id]
                fk = True
        elif col == 'parkkey' and len(val) and table != 'parks':
            if not len(val): # If col exists, but is empty
                values.append(None)
            else:
                query = 'SELECT ID FROM parks WHERE parkkey = %s;'
                vals = [val]
                fk = True
        elif col == 'divID':
            if not len(val): # If col exists, but is empty
                values.append(None)
            else:
                query = '''SELECT ID FROM divisions
                           WHERE divID = %s AND lgID = %s;'''
                try:
                    lg_id = orig_values[list(csv_cols).index('lgID')]
                except:
                    print(query, list(csv_cols), csv_cols, orig_values, sep='\n', end='\n\--------------n')
                vals = [val, lg_id]
                fk = True

        if fk:
            try:
                cursor_select = connection.cursor()
                cursor_select.execute(query, vals)
                result = cursor_select.fetchone()
                if not result:
                    # No matching record
                    msg = f'''Tried to get ID to match {col}, but
                        * No matching record for {vals} in {table}.
                        * {orig_values}
                        * {csv_cols}'''
                    print(msg)
                    log(msg)
                    return None
                else:
                    values.append(result[0])
                cursor_select.close()
            except TypeError:
                print(query, vals)
                raise
            except:
                print(query, vals)
                raise

    return values

def insert_records(table, cursor, connection):
    """Inserts records in CSV into matching MySQL table."""
    csv = f'csvs/{table}.csv'
    
    df = pd.read_csv(csv, keep_default_na=False)

    columns = get_columns(df.columns, table)
    str_columns = ','.join(columns)

    placeholders = ','.join(['%s' for i in range(len(columns))])

    insert = f'INSERT INTO  {table} ({str_columns}) VALUES ({placeholders})'

    for df_row in df.iterrows():
        row = df_row[1]
        values = get_values(row.to_list(), df.columns, table, connection)
        if not values: # Something went wrong in get_values()
            continue
        try:
            cursor.execute(insert, values)
        except mysql.connector.errors.IntegrityError as e:
            log(f'Not inserting {values} into {table}.')
            log('\t * ' + str(e))
        except:
            print(insert, values, sep='\n', end='\n----------\n')
            raise

def main():
    start_time = time.perf_counter()
    clear_log()
    log(f'Start Time: {start_time}')

    connection = db_connect()
    cursor = connection.cursor()

    print('Creating database.')
    start_time_create_db = time.perf_counter()
    create_db(cursor)
    end_time_create_db = time.perf_counter()
    time_create_db = end_time_create_db - start_time_create_db
    print(f'Created database in {time_create_db} seconds.')
    log(f'Time to create database: {time_create_db} seconds')

    cursor.execute('use lahmansbaseballdb;')
    cursor.close()

    tables = get_tables()
    for table in tables:
        cursor = connection.cursor(prepared=True)
        start_time_pop_table = time.perf_counter()
        print(f'Populating {table}.')
        insert_records(table, cursor, connection)
        end_time_pop_table = time.perf_counter()
        time_pop_table = end_time_pop_table - start_time_pop_table
        print(f'Finished populating {table} in {time_pop_table} seconds.')
        log(f'Time to populate {table}: {time_pop_table} seconds')
        cursor.close()

    
    connection.commit()
    cursor.close()
    connection.close()
    end_time = time.perf_counter()
    log(f'End Time: {end_time}')
    total_time = end_time - start_time
    total_minutes = round(total_time/60, 2)
    print(f'Phew! That took {total_minutes} minutes.')
    log(f'Total minutes to execute script: {total_minutes}')

main()