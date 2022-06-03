import subprocess
from configuration import config

def dump(db: str, dst: str, output:str='', excluded_data: list=[]) -> bool:
    tool = config.pg_dump()
    
    args = [ tool, '--format', 'directory', '--no-password','--jobs', '4', 
    '--blobs', '--encoding', 'UTF8', '--verbose','--file', dst, '--dbname', db]

    args = excluding_args(args, excluded_data)
    
    if output == '':
        output = subprocess.PIPE

    ps = subprocess.Popen(args, stdout=output, stderr=output)
    exit_code = ps.wait()

    if int(exit_code) != 0:
        return False, f'Dumping failed. Return code : {exit_code}'

    return True, ''

def excluding_args(args:list, excluded_data:list)->list:
    for tb in excluded_data:
        args.append('--exclude-table-data')
        args.append(tb)

    return args
