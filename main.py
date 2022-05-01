import backup, psql, filesystem, notify, os 
from datetime import datetime
from dotenv import load_dotenv
import shutil
import subprocess

def main():
    databases = psql.databases()
    root_path = generate_root_path()     
    for db in databases:
        handle_database(db, root_path)    

    archive_path = f'{root_path}.zip'
    ok, err_desc = compress_backup(root_path, archive_path)
    if not ok:
        send_email_error(err_desc) 
    
    if backup.use_network_storage():
        copy_backup_to_network_storage()
    else:
        pass

def copy_backup_to_network_storage(archive_path:str):

    archive = os.path.basename(archive_path)

    connected, backup_path = backup.check_network_directory()
    
    if connected:

        if filesystem.is_enough_free_space_for_file(archive_path, backup_path):
            shutil.copyfile(archive_path, f'{backup_path}\\{archive}')
        else:
            pass
    else:
        pass
    
    clear_old_copy(backup_path)
        
def clear_old_copy(path:str):
    days_for_save = os.getenv('COUNTBACKUP')
    if days_for_save != None:
        count = int(days_for_save)
        filesystem.remove_old_backup(path, count)

def compress_backup(src: str, dst:str):
    utill = os.getenv('COMPRESSUTIL')
    returncode = subprocess.Popen( [ utill, 'a', '-tzip', '-mx5', dst, src],stdout=subprocess.PIPE).wait()

    if int(returncode) != 0:
        return False, 'Compressing failed. Return code : {}'.format(returncode)
    return True, ''

def handle_database(db:dict, root_path:str)->bool:
    
    if not backup.check_filesystem_before_backup(db, root_path):
        send_email_error('Not enoght free space')
        return False
    
    name = db['name']
    backup_path = f'{root_path}\\{name}'
    
    try: 
        if psql.dump_db(name, backup_path):
            return True
        else:
            send_email_error('Backuping wasn\'t successful')
            return False
    except Exception as ex:
        send_email_error("Backuping was end exception situation.Check logs")

def send_email_error(msg: str)->bool:
    email_from = os.getenv("EMAILFROM")
    password = os.getenv('EMAILPASSWORD')
    emails_to = os.getenv('EMAILTO').split(',')
    subject = os.getenv('EMAILSUBJECT')

    notify.EmailLetter(
        notify.EmailUser(login=email_from, password=password),
        body=msg,
        subject=subject, 
        name='Backup').send(emails_to)

def generate_root_path()-> str:
    now = datetime.now()
    now_format = now.strftime("%d-%m-%Y")
    backpath = os.getenv("BACKLOCALPATH")
    today_back = f'{backpath}\\{now_format}'
    
    if not os.path.exists(today_back):
        os.mkdir(today_back)
    
    return today_back

if __name__ == '__main__':
    load_dotenv('env')
    main()

