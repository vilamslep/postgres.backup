from email.utils import formatdate
from msilib.schema import MIME
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


class EmailUser:
    def __init__(self, login:str, password:str, smtp_server:str, smtp_port:int) -> None:
        self.login = login
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
    
class EmailLetter:
    user: EmailUser
    message: MIMEMultipart
    recivers: list[str]

    def __init__(self, user:EmailUser, body:str, subject:str, name:str, recivers:list) -> None:
        self.user = user
        
        self.message = MIMEMultipart()
        self.message['From'] = f'{name} <{user.login}>'
        self.message['To'] = ''.join(recivers)
        self.message['Date'] = formatdate(localtime=True)
        self.message['Subject'] = subject

        self.recivers = recivers
        self.message.attach(MIMEText(body, 'html'))

    def send(self): 
        server = self.get_smtp_server()
        
        for to in self.recivers:
            server.sendmail(self.user.login, to, self.message.as_string())
        
        server.quit()

    def get_smtp_server(self):
        server = smtplib.SMTP(self.user.smtp_server, self.user.smtp_port)
        server.ehlo()
        server.starttls()
        server.login(self.user.login, self.user.password)

        return server
