'''
Simple library to send email using GMail

Source: paulchakravarti/gmail-sender project
Link:   https://github.com/paulchakravarti/gmail-sender
'''
from gmail.gmail import GMail
from gmail.message import Message
import config_loader as config

def send_notice(username, password, subject, to, text):
    gmail = GMail(username, password)
    msg = Message(subject=subject, to=to, cc=None, bcc=None, text=text)
    gmail.send(msg)
    gmail.close()

def error_notice(timestamp, project, error, executor):
    message = "Exception received by %s on %s." % (executor, timestamp)
    message += "Project:\t%s" % (project)
    message += "Exception:\t%s" % (error)

    for recipient in config.get('NOTIFY'):
        notifier.send_notice(   config.get('GMAIL_AUTH')['username'], 
                                config.get('GMAIL_AUTH')['password'], 
                                "CS569_FinalProject failure detected", 
                                recipient, message)