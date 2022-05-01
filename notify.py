from email import message
from msilib.schema import MIME
from ntpath import join
from re import sub
import smtplib
from email.mime.text import MIMEText

class EmailUser:
    def __init__(self, login:str, password:str) -> None:
        self.login = login
        self.password = password
    


class EmailLetter:
    user: EmailUser
    message: MIMEText

    def __init__(self, user:EmailUser, body:str, subject:str, name:str) -> None:
        self.message = MIMEText(body)
        self.message['Subject'] = subject
        self.message['From'] = f'{name} <{user.login}>'
        
    def send(self, recivers:list): 
        server = self.get_smtp_server()

        self.message['To'] = ''.join(recivers)
        for to in recivers:
            server.sendmail(self.user.login, to, self.message.as_string())
        
        server.quit()

    def get_smtp_server(self):
        server = smtplib.SMTP('smtp.yandex.ru', 587)
        server.ehlo()
        server.starttls()
        server.login(self.user.login, self.user.password)

        return server    


# def send_email(email: str, password: str, sender_name, to: list, subject: str, body:str ):
#     server = smtplib.SMTP('smtp.yandex.ru', 587)
#     server.ehlo() 
#     server.starttls()
#     server.login(email, password)
#     msg = MIMEText(body)
#     msg['Subject'] = subject
#     msg['From'] = f'{sender_name} <{email}>'
#     msg['To'] = ''.join(to)
#     for t in to:
#         server.sendmail( email, t, msg.as_string() )
#     server.quit()

