import smtplib

from email.mime.multipart import MIMEMultipart

from email.mime.text import MIMEText
import os

def sendmail(subject, msg_body, to_adr, from_email=''):
    # pdb.set_trace()
    if from_email =='':
        from_adr = os.environ.get('email_address') # secrets['FROM_EMAIl']
    login_adr = from_adr
    # second_email = secrets['SECOND_EMAIL']
    # third_email = secrets['THIRD_EMAIL']
    smtpmsg = MIMEMultipart()
    smtpmsg['From']=from_adr

 

    smtpmsg['To']=to_adr
    smtpmsg['Subject']= subject
    # msgbody = msg_body

 

    msgbody = MIMEText(msg_body)
    server = smtplib.SMTP(os.environ.get('Email_Host'), 587)
    #server.ehlo()
    server.starttls()
    #server.ehlo()
    server.login(login_adr, os.environ.get('password'))
    server.ehlo()
    smtpmsg.attach(msgbody)
    # text = smtpmsg.as_string()
    server.send_message(smtpmsg)
    server.quit()

sendmail("transaction successful","trrrrrrrrrrrr","routanshuman01@gmail.com")
# print(os.environ.get('Email_Host'),os.environ.get("email_address"),os.environ.get("password"))