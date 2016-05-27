from gmail.gmail import GMail
from gmail.message import Message

def send_notice(username, password, subject, to, text):
    gmail = GMail(username, password)
    msg = Message(subject, to, text)
    gmail.send(msg)
    gmail.close()