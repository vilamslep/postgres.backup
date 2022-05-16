import conf, compress, json, filesystem, notify 
from os import getenv, listdir, system as exe
from os.path import isdir
from postgres import pg_dump,psql
from postgres.psql import Database
from loguru import logger

def start():
    
    setup_logger()

    logger.info("start of backup")

    databases = psql.databases()

    ldb = list(map(lambda x: x.name, databases))
    logger.info("databases for backuping: " + ", ".join(ldb))
    
    rpath = filesystem.generate_root_path(conf.backpath())
    
    logger.info(f'create root path: {rpath}')
    
    errors = list()
    for db in databases:
        excluded_tables = psql.excluded_tables(db.name)
        
        if len(excluded_tables) > 0:
            logger.info("excluded tables: " + ", ".join(excluded_tables))
        
        ok, msg = handle_database(db, rpath, excluded_tables)    

        if not ok:
            errors.append(msg)
            logger.error(f'backuping of \'{db.name}\' is not success. {msg}')
        else:
            logger.info(f'backuping of \'{db.name}\' is success')

    if len(errors) > 0:
        log_dir = 'log\\'
        ls = listdir(log_dir)
        ls = list(map(lambda x: log_dir + x, ls))
        send_email_error('\n'.join(errors), ls)

    logger.info("finish of backup")

def handle_database(db:Database, rpath:str, excluded_tables:list)->bool:
    logger.info(f'start handling of \'{db.name}\'')
    logger.info('check free space')

    try:
        if not check_free_space(db, rpath):
            return False, 'Not enoght free space'
    except Exception as ex:
        logger.error('checking of free space end with error')
        return False, ex

    logger.info('success') 

    child_dirs = ['logical']
    if len(excluded_tables) > 0:
        child_dirs.append('binary')

    logger.info('generate children directories')

    try:
        locations = filesystem.generate_directories(rpath, db.name, child_dirs)
    except Exception as ex:
        logger.error('generating of directories end with error')
        return False, ex

    logger.info('success')

    logger.info('start dumping')

    fout = f'log\\{db.name}.log'
    out = open(fout, 'w', encoding='utf-8')
    ok, msg = pg_dump.dump(db.name, locations['logical'],out, excluded_tables)
    out.flush()
    out.close()

    if not ok:
        logger.error(f'dumping of \'{db.name}\' end with error')
        return ok, msg

    are_there = are_there_errors_in_dumping_log(fout)

    if are_there:
        return False, "there are errors in dumping file"
    else:
        filesystem.remove(fout)

    logger.info('success')
    
    logger.info('start to unload table as binary data')

    binaryes_files = list()
    for table in excluded_tables:
        path = locations['binary']
        table_path = f'{path}\\{table}'
        
        logger.info(f'unload \'{db.name}.{table}\' to {table_path}')
        
        try:
            ok = psql.copy_binary(db.name, table, table_path)['to']()
        except Exception as ex:
            logger.error(f'unloading of \'{db.name}.{table}\' to end with error')
            return False, ex

        if not ok:
            return False, f'unloading of \'{db.name}.{table}\' is not success'
        
        logger.info('success')
        
        binaryes_files.append({table:table_path})

    try:
        data = { 'data': { 'tables' : binaryes_files } } 
        fmap = locations['main'] + '\\map.json'
        write_map_file(data, fmap)
    except Exception as ex:
        logger.error(f'writing of map data for restore to file is not success')
        return False, ex
    
    path_back_db = locations['main']
    archive = f'{path_back_db}.zip' 
    
    logger.info(f'Start to compress. The archive {archive}')

    try:
        ok = compress.compress_dir(path_back_db, archive)
    except Exception as ex:
        logger.error(f'compressing is not success')
        return False, ex        

    if not ok:
        return ok, f'compressing is not success'
    
    logger.info('success')

    logger.info(f'start to remove {path_back_db}')

    try:
        filesystem.remove(path_back_db)
    except Exception as ex:
        logger.error(f'removing is not success')
        return False, ex        

    return True, ''

def check_network_directory(to_mount:bool = True) -> bool:
    storage = conf.net_storage()
    path = storage['path'] 
    user = storage['user']
    password = storage['password']
    
    if isdir(path):
        return True, path
    elif not to_mount:
        return False, ''
    
    cmd = f'net use /user:{user} {path} {password}' 
    exe(cmd)

    return check_network_directory(False)

def check_free_space(db:Database , rpath:str)->bool:
    data_location = conf.database_location()
    path = f'{data_location}\\base\\{db.oid}'

    return filesystem.is_enough_free_space(path, rpath, True)

def use_network_storage()->bool:
    network_storage = getenv('BACKUPNETPATH')
    return network_storage != None        

def setup_logger():
    logger.add(filesystem.path_for_logging(),level='INFO')

def write_map_file(data:dict, file:str)->None:
    with open(file=file,mode='w') as w:
        w.write( json.dumps(data,ensure_ascii=True,indent=4) )

def are_there_errors_in_dumping_log(file:str)->bool:
    errors = conf.error_lang()
    with open(file, mode='r', encoding='cp1251') as f:
        ln = f.readline()
        while ln != '':
            for i in errors:
                if ln.find(i) != -1:
                    return True

            ln = f.readline()
    return False

def send_email_error(msg: str, files:list)->bool:
    setting = conf.email()
    
    email_user = notify.EmailUser(login=setting['email_from'], password=setting['password']) 
    notify.EmailLetter(
        user=email_user,
        body=msg,subject=setting['subject'],
        name='Backup',
        recivers=setting['emails_to'],
        files=files
    ).send()
