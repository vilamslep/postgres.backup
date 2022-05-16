from os import getenv

net_storage = {
    'path'      :'BACKUPNETPATH',
    'user'      :'BACKUPUSER',
    'password'  :'BACKUPPASSWORD'
}

storage = {
    "path": "BACKLOCALPATH",
    "db_path":"PGDATA"
}

psql = {
    'user'  :'PGUSER',
    'password'  :'PGPASSWORD',
    'tool'      : 'PGBACKUPTOOL',
}

email = {
    'email_from': 'EMAILFROM',
    'password'  : 'EMAILPASSWORD',
    'emails_to' : 'EMAILTO',
    'subject'   : 'EMAILSUBJECT'
}

tools = {
    "pg_dump": "PGDUMPUTIL",
    "psql": "PSQLUTIL",
    "compress" : "COMPRESSUTIL"
}

class Environment:
    def get_net_storage_setting():
        return Environment.__create_dict_with_environment_vars(net_storage)

    def get_storage_setting():
        return Environment.__create_dict_with_environment_vars(storage)

    def get_psql_setting():
        return Environment.__create_dict_with_environment_vars(psql)

    def get_email_setting():
        return Environment.__create_dict_with_environment_vars(email)

    def tools():
        return Environment.__create_dict_with_environment_vars(tools)

    def __create_dict_with_environment_vars(setting:dict)->dict:
        d = dict()
        for k,v in setting.items(): 
            d[k] = getenv(v)
        return d