from datetime import datetime
import os, psutil, shutil

def generate_root_path(path:str)-> str:
    now = datetime.now()
    now_format = now.strftime("%d-%m-%Y")
    today_back = f'{path}\\{now_format}'
    
    __create_if_not_exists(today_back)
    
    return today_back

def generate_directories(root:str, name:str, children:list=[])->dict:
    locations = dict()

    path = f'{root}\\{name}'
    __create_if_not_exists(path)

    locations['main'] = path

    for child in children:
        child_path = f'{path}\\{child}'
        __create_if_not_exists(child_path)
        locations[child] = child_path
    
    return locations
    
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

def remove(path:str):
    __remove_file(path)

def path_for_logging()->str:
    now = datetime.now().strftime("%d-%m-%Y")
    return f'log\\{now}.log'

def is_enough_free_space(src: str, dst:str, its_directory=False) -> bool:
    free = psutil.disk_usage(dst).free

    if its_directory:
        size = __get_size(src)
    else:
        size = os.path.getsize(src)

    return free > size

def __create_if_not_exists(path:str)->None:
    if not os.path.exists(path):
        os.mkdir(path)

def __remove_file(path: str):
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

def __get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        ffn = lambda f: not os.path.islink(f) 
        files = list( map( lambda f: os.path.join(dirpath, f), filenames ) ) 
        try:
            total_size += sum( map( os.path.getsize, filter(ffn, files) ) )
        except FileNotFoundError:
            continue
        
    return total_size