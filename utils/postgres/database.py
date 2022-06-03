class Database:
    name: str
    oid = str

    def __init__(self, name:str, oid:str) -> None:
        self.name = name
        self.oid = str(oid)

