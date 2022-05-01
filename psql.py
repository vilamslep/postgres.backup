import os, subprocess, psycopg2
from contextlib import closing
import backup

class Database:
    def __init__(self, name:str, oid:str) -> None:
        self.name = name
        self.oid = oid

def dump_db(db: str, dst: str ) -> bool:
    tool = backup.tool()
    
    args = [ tool, '--format', 'directory', '--no-password','--jobs', '4', 
    '--blobs', '--encoding', 'UTF8', '--verbose','--file', dst, '--dbname', db]

    returncode = subprocess.Popen(args, stdout=subprocess.PIPE).wait()

    if int(returncode) != 0:
        return False, f'Dumping failed. Return code : {returncode}'

    return True, ''

def databases() -> list[Database]:
    dbs = list()
    conn = backup.init_default_db_connection()

    with closing(psycopg2.connect(dbname=conn.db, user=conn.user, password=conn.password, host=conn.host)) as conn:
        
        with conn.cursor() as cursor:
            cursor.execute( txt_custom_databases() )
            fn = lambda x: Database(x[0], x[1])
            dbs = list(map( fn, cursor.fetchall() ))

    return dbs

def txt_custom_databases()->str:
    return '''
        SELECT datname, oid 
        FROM pg_database 
        WHERE NOT datname IN (\'postgres\', \'template1\', \'template0\');
        '''
