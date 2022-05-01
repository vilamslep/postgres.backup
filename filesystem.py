import os, psutil
import shutil

def remove_old_backup(backup_path: str, count: int) -> bool:
        
    os.chdir(backup_path)
    
    files = os.listdir(backup_path)
    files.sort(key=os.path.getmtime)
    
    need_to_delete = len(files) - count
    if need_to_delete > 0:
        for i in range(need_to_delete):
            file = files.pop(0)
            try:
                __remove_file(f'{backup_path}\\{file}')
            except:
                return False
    
    return True

def is_enough_free_space_for_db(db: dict, dir:str) -> bool:
    path_data = os.getenv('PGDATA')
    oid = db['oid']
    
    path = f'{path_data}\\base\\{oid}'
    total_size = __get_size(path)
    
    free = psutil.disk_usage(dir).free

    return free > total_size

def is_enough_free_space_for_file(file:str, dst:str):
    pass

def __remove_file(path: str):
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

def __get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size