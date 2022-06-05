from datetime import datetime
from os.path import basename
from utils.postgres import Database, excluded_tables, dump, copy_binary 
from utils import compress_dir
import fs, sys, json
from configuration import config
from loguru import logger

class BackupItem:
    database: Database   
    status: str
    start_time: datetime
    end_time: datetime
    size_database: float
    size_backup: float
    backup_path: str
    details: str

    def __init__(self, database: Database) -> None:
        self.database = database

    def backup(self, tempdir: str, targetdir: str ) -> None:
        if len(self.database.oid) == 0:
            self.status = 'warning'
            self.details = 'oid is empty. Database isn\'t found in server'
            return
        self.start_time = datetime.now()
        self.__set_db_size()
        self.details = ''
        try:    
            self.__backup(tempdir, targetdir)
        except Exception:
            exc_info = sys.exc_info()
            
            self.details = exc_info[1]
            self.status = 'error'
            self.end_time = datetime.now()

            raise Exception(f'backup of {self.database.name} is failed').with_traceback(exc_info[2])
        
        self.status = 'success'
        self.end_time = datetime.now()

    def __backup(self, tempdir: str, targetdir: str ) -> bool:
        logger.info('checking space in template directory')
        
        if not self.__check_space_for_backup(tempdir):
            raise Exception(f'there isn\'t enought space in disk. checking path is {tempdir}')
            
        logger.info('success')     
        logger.info('checking space in target directory')
        if not self.__check_space_for_backup(targetdir):
            raise Exception(f'there isn\'t enought space in disk. checking path is {targetdir}')
        
        logger.info('success') 

        chdir = ['logical']

        exclude_tabls = excluded_tables(self.database.name)

        if len(exclude_tabls) > 0:
            logger.info('excluded tables are ' + ','.join(exclude_tabls))
            chdir.append('binary')

        try:
            locations = fs.generate_directories(tempdir, self.database.name, chdir)
        except:
            trace = sys.exc_info()[2]
            raise Exception('generating of directories end with error').with_traceback(trace)

        logger.info('dumping...')
        self.__dump(locations['logical'], exclude_tabls)
        logger.info('success')

        if len(exclude_tabls) > 0:
            logger.info('uploading binary data')
            binaries_files = self.__unload_as_binary(locations['binary'], exclude_tabls)
            self.__write_restore_file(locations['main'], binaries_files)
            logger.info('success')
        
        path_back_db = locations['main']
        archive = f'{path_back_db}.zip' 

        logger.info('compressing...') 
        if not compress_dir(path_back_db, archive):
            raise Exception('compressing is not success')
        logger.info('success')


        logger.info('coping backup to target directory')
        try:
            dst_name = basename(archive)
            self.backup_path = f'{targetdir}\\{dst_name}'
            fs.copy_file(archive, self.backup_path)
            self.size_backup = fs.get_size(self.backup_path)
        except:
            trace = sys.exc_info()[2]
            raise Exception('can\'t copy the backup to target directory').with_traceback(trace)
        logger.info('success')

        logger.info('removing temp files')
        try:
            fs.remove(path_back_db)
            fs.remove(archive)
        except:
            trace = sys.exc_info()[2]
            raise Exception(f'removing is not success').with_traceback(trace)
        logger.info('success')

    def __check_space_for_backup(self, path:str) -> bool:
        try:
            dbs_store = config.database_location()
            dbstore = f'{dbs_store}\\base\\{self.database.oid}'
            ok = fs.is_enough_space(dbstore, path)
        except Exception as ex:
            logger.error(ex)

            trace = sys.exc_info()[2]
            raise Exception("checking free space is failed").with_traceback(trace)

        return ok
    def __set_db_size(self):
        dbs_store = config.database_location()
        dbstore = f'{dbs_store}\\base\\{self.database.oid}'
        self.size_database = fs.get_size(dbstore)

    def __dump(self, lpath: str, exclude_tabls:list) -> None:
        fout = f'log\\{self.database.name}.log'
        out = open(fout, 'w', encoding='utf-8')
        ok, msg = dump(self.database.name, lpath, out, exclude_tabls)
        out.flush()
        out.close()

        if not ok:
            raise Exception(msg)

        are_there_errs = self.__are_there_errors_in_dumping_log(fout)

        if are_there_errs:
            raise Exception('there are errors in dumping file')
        else:
            fs.remove(fout)

    def __are_there_errors_in_dumping_log(self, file:str)->bool:
        errors = config.errors()
        with open(file, mode='r', encoding='cp1251') as f:
            ln = f.readline()
            while ln != '':
                for i in errors:
                    if ln.find(i) != -1:
                        return True

                ln = f.readline()

        return False

    def __unload_as_binary(self, bpath:str, tabls:list) -> list:
        binfiles = list()
        for table in tabls:
            table_path = f'{bpath}\\{table}'
            
            try:
                ok = copy_binary(self.database.name, table, table_path)['to']()
            except Exception as ex:
                raise Exception(f'unloading of \'{self.database.name}.{table}\' to end with error').with_traceback(sys.exc_info[2])

            if not ok:
                raise Exception(f'unloading of \'{self.database.name}.{table}\' is not success')
            
            binfiles.append({table:table_path})

        return binfiles

    def __write_restore_file(self, mpath: str, binfiles: list) -> None:
        data = { 'data': { 'tables' : binfiles } } 

        f = f'{mpath}\\map.json'
        with open(file=f, mode='w') as w:
            w.write( json.dumps(data, ensure_ascii=True, indent=4) )
