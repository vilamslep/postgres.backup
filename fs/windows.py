from datetime import datetime
import os
from os.path import isdir
from configuration import Periodicity
from fs.common import remove, create_if_not_exists
from configuration import config

def get_root_dir(path:str, name:str, kind: Periodicity)-> str:
    today = datetime.now()
    
    if kind == Periodicity.DAILY:
        fmt = today.strftime("%d-%m-%Y")
    elif kind == Periodicity.WEEKLY:
        fmt = today.isocalendar().week
    elif kind == Periodicity.MONTHLY:
        fmt = today.month

    back_path = f'{path}\\{name}\\{fmt}'
    
    if path[0:2] == '\\\\':
        if not __check_network_directory(path):
            raise Exception('can\'t connect network directory') 

    create_if_not_exists(back_path)
    
    return back_path

def generate_directories(root:str, name:str, children:list=[])->dict:
    locations = dict()

    path = f'{root}\\{name}'
    create_if_not_exists(path)

    locations['main'] = path

    for child in children:
        child_path = f'{path}\\{child}'
        create_if_not_exists(child_path)
        locations[child] = child_path
    
    return locations
    
def clear_old_backup(backup_path: str, count: int) -> bool:

    cur_dir = os.path.realpath('.')

    os.chdir(backup_path)
    
    files = os.listdir(backup_path)
    files.sort(key=os.path.getmtime)
    
    need_to_delete = len(files) - count
    if need_to_delete > 0:
        for i in range(need_to_delete):
            file = files.pop(0)
            try:
                remove(f'{backup_path}\\{file}')
            except:
                return False
    
    os.chdir(cur_dir)
    
    return True

def __check_network_directory(path:str, to_mount:bool = True) -> bool:
    auth = config.target_folder_auth()
    user = auth['user']
    password = auth['password']
    
    if isdir(path):
        return True
    elif not to_mount:
        return False
    
    cmd = f'net use /user:{user} {path} {password}' 
    os.system(cmd)

    return __check_network_directory(False)

