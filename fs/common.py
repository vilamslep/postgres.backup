import os, psutil, shutil
from shutil import rmtree
from os.path import isdir

WIN_OS_PROGDATA = 'C:\Temp\postgres.backup'

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        ffn = lambda f: not os.path.islink(f) 
        files = list( map( lambda f: os.path.join(dirpath, f), filenames ) ) 
        try:
            total_size += sum( map( os.path.getsize, filter(ffn, files) ) )
        except FileNotFoundError:
            continue
        
    return total_size

def remove(path: str):
    if os.path.isdir(path):
        rmtree(path)
    else:
        os.remove(path)

def temp_dir() -> str:
    create_if_not_exists(WIN_OS_PROGDATA)
    return WIN_OS_PROGDATA

def is_enough_space(src: str, dst:str) -> bool:
    free = psutil.disk_usage(dst).free

    if isdir(src):
        size = get_size(src)
    else:
        size = os.path.getsize(src)

    return free > size

def create_if_not_exists(path:str)->None:
    os.makedirs(path, exist_ok=True)

def copy_file(src:str, dst:str) -> None:
    shutil.copyfile(src, dst)