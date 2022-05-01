from logging import root
from os import getenv, system as cmd
from os.path import isdir
from re import M
from filesystem import check_free_space_by_db, is_enough_free_space_for_db


class Connection:
    def __init__(self, user:str, password:str, db:str, host:str, port:int  ) -> None:
        self.user = user
        self.password = password
        self.db = db
        self.host = host
        self.port = port
        

env_net_path = {
    'path':'BACKUPNETPATH',
    'user':'BACKUPUSER',
    'password':'BACKUPPASSWORD'
}

env_psql = {
    'user':'PGUSER',
    'password':'PGPASSWORD',
    'tool': 'PGBACKUPTOOL',
}

def check_network_directory() -> bool:
    BACKUP_REPOSITORY_PATH = getenv(env_net_path['path']) 
    BACKUP_REPOSITORY_USER_NAME = getenv(env_net_path['user'])
    BACKUP_REPOSITORY_USER_PASSWORD = getenv(env_net_path['password'])
    
    backup_storage_available = isdir(BACKUP_REPOSITORY_PATH)
    if backup_storage_available:
        return True, BACKUP_REPOSITORY_PATH
    
    mount_command = f'net use /user:{BACKUP_REPOSITORY_USER_NAME} {BACKUP_REPOSITORY_PATH} {BACKUP_REPOSITORY_USER_PASSWORD}' 
    
    cmd(mount_command)
    
    backup_storage_available = isdir(BACKUP_REPOSITORY_PATH)

    if backup_storage_available:
        return True, BACKUP_REPOSITORY_PATH
    else:
        return False, ''

def check_filesystem_before_backup(db: dict, root_path:str)->bool:
    return is_enough_free_space_for_db(db, root_path)

def use_network_storage()->bool:
    network_storage = getenv('BACKUPNETPATH')
    return network_storage != None        

def init_default_db_connection()->Connection:
    return Connection(getenv(env_psql['user']), getenv(env_psql['password']), 'postgres', 'localhost', 5432)

def tool()->str:
    return getenv('PGBACKUPTOOL')