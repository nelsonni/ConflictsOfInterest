from datetime import datetime
from gmail.gmail import GMail
from gmail.message import Message

def send_notice(crash_datetime, crash_message):
	datetime.time(crash_datetime)

def test_notice():
	gmail = GMail(	username="",
					password="")
	msg = Message(	subject="",
					to="",
					text="TESTING!!!")
	gmail.send(msg)
	gmail.close()