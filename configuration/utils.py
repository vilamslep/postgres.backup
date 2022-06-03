class Utils:
    dump: str
    psql: str
    compress: str

    def __init__(self, conf: dir) -> None:
        self.dump = conf['dump']
        self.psql = conf['psql']
        self.compress = conf['compress']
