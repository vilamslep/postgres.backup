class Folder:
    path: str
    user: str
    password: str

    def __init__(self, conf: dir) -> None:
        self.path       = conf['path']
        self.user       = conf['user']
        self.password   = conf['password']
