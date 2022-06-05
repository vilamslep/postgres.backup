class Email:
    user: str
    password: str
    smtp_host: str
    smtp_port: str
    recivers: list
    letter: dict

    def __init__(self, conf: dir) -> None:
        self.user       = conf['user']
        self.password   = conf['password']
        self.smtp_host  = conf['smtp_host']
        self.smtp_port  = conf['smtp_port']
        self.recivers   = conf['recivers']
        self.letter     = conf['letter']