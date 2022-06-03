from operator import truediv
import subprocess, psycopg2
from contextlib import closing
from configuration import config 
from utils.postgres.database import Database

def databases(dbs_filter:list = []) -> list[Database]:
    dbs = list()
    with closing(config.get_connection(psycopg2.connect,'postgres')) as conn:
        with conn.cursor() as cursor:
            cursor.execute( txt_custom_databases(dbs_filter) )
            fn = lambda x: Database(x[0], x[1])
            dbs = list(map( fn, cursor.fetchall() ))

    return dbs

def excluded_tables(db: str) -> list[str]:
    tables = list()
    with closing(config.get_connection(psycopg2.connect,db)) as conn:
        with conn.cursor() as cursor:
            cursor.execute( txt_stat_tables() )
            tables = [item[0] for item in cursor.fetchall() ] 

    return tables

def copy_binary(db:str, src:str, dst:str)->dict:
    
    tool = config.psql()
    
    args = [tool, '--dbname', db]

    def __from()->bool:
        path_from = __prepare_path(src)

        cmd = ["COPY", dst, "TO", path_from, "WITH BINARY;"]

        return __execute(args, " ".join(cmd)) == 0     

    def __to()->bool:
        path_save = __prepare_path(dst)    
        
        cmd = ["COPY", src, "TO", path_save, "WITH BINARY;"]
        return __execute(args, " ".join(cmd)) == 0
        
    def __prepare_path(path:str)->str:
        npath = path.replace("\\", "\\\\")
        return f'\'{npath}\''

    def __execute(args:list, command:str)->int:
        args.append('--command')
        args.append(command)
        
        exit_code = subprocess.Popen(args, stdout=subprocess.PIPE).wait()
        return int(exit_code)

    return {"from":__from, "to": __to}

def txt_custom_databases(dbs:list)->str:
    if len(dbs) > 0:
        txtdb = ','.join(list(map(lambda x: f'\'{x}\'',dbs)))
        filter = f'WHERE datname IN( {txtdb} )'
    else:
        filter = 'WHERE NOT datname IN (\'postgres\', \'template1\', \'template0\')'

    return 'SELECT datname, oid FROM pg_database {};'.format(filter)

def txt_stat_tables() -> str:
    '''select tables which are bigger that 4 GB'''
    return '''
    SELECT table_name as name
    FROM (
	    SELECT table_name,pg_total_relation_size(table_name) AS total_size
	    FROM (
		    SELECT (table_schema || '.' || table_name) AS table_name 
            FROM information_schema.tables) AS all_tables
 	ORDER BY total_size DESC) AS pretty_sizes WHERE total_size > 4294967296;
    '''