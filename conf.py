from backup.env import Environment

def psql()-> str:
    return Environment.tools()['psql']

def pg_dump()->str:
    return Environment.tools()['pg_dump']

def db()->dict:
    return Environment.get_psql_setting()

def email()->dict:
    setting = Environment.get_email_setting()
    setting['emails_to'] = setting['emails_to'].split(',')
    return setting

    
def net_storage()->dict:
    return Environment.get_net_storage_setting()

def compress_tool()->str:
    return Environment.tools()['compress']

def backpath()->str:
    return Environment.get_storage_setting()['path']

def database_location()->str:
    return Environment.get_storage_setting()['db_path']

def error_lang()-> list[str]:
    return ['ошибка', 'erorr'] 