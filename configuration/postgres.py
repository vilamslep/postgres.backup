from os import environ

class Postgres:
    user: str
    password: str
    host: str
    port: int
    data_location: str

    def __init__(self, conf: dir) -> None:
        self.host           = conf['host']
        self.port           = conf['port']
        self.user           = conf['user']
        self.password       = conf['password']
        self.data_location  = conf['data_location']

    def load_envs(self):
        environ['PGUSER']       = self.user
        environ['PGPASSWORD']   = self.password
        environ['PGHOST']       = self.host
        environ['PGPORT']       = self.port
    
    #fn_connect is function for creating connection with DBMS
    def create_connection(self, fn_connect, db: str):
        return fn_connect(dbname=db, 
            user=self.user, 
            password=self.password, 
            host=self.host, 
            port=self.port)   