import conf

class Socket:
    ipv4: str
    port: int

    def __init__(self, address:str, port:int):
        self.ipv4 = address
        self.port = port

class BasicAuth:
    user: str
    password: str

    def __init__(self, user:str, password:str):
        self.user = user
        self.password = password

class DBConnectionSetting:
    socket: Socket
    auth: BasicAuth
    db: str 

    def __init__(self, socket: Socket, auth: BasicAuth, db:str):
        self.socket = socket
        self.auth = auth    
        self.db = db 

    def create_connection(self, fn_connect):
        return fn_connect(dbname=self.db, 
            user=self.__user(), 
            password=self.__password(), 
            host=self.__host(), 
            port=self.__port())   

    def __user(self)->str:
        return self.auth.user

    def __password(self)->str:
        return self.auth.password

    def __host(self)->str:
        return self.socket.ipv4
    
    def __port(self)->int:
        return self.socket.port

def new(db:str)->DBConnectionSetting:
    setting = conf.db()
    
    return DBConnectionSetting(
        Socket('localhost', 5432),
        BasicAuth(setting['user'], setting['password']),
        db)