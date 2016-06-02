from gmail.gmail import GMail
from gmail.message import Message

def send_notice(username, password, subject, to, cc, text):
    gmail = GMail(username, password)
    msg = Message(subject, to, cc, text)
    gmail.send(msg)
    gmail.close()