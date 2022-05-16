import subprocess
import conf
def compress_dir(src:str, dst)->bool:
    utill = conf.compress_tool()
    
    exit_code = subprocess.Popen( [ utill, 'a', '-tzip', '-mx5', dst, src],stdout=subprocess.PIPE).wait()

    return int(exit_code) == 0
