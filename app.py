from flask import Flask,render_template,request,flash,redirect,url_for,session
from forms import AccountOpeningForm
import smtplib
import ssl
from email.message import EmailMessage
import os
import smtplib
from datetime import datetime
import random
from email.mime.multipart import MIMEMultipart
import logging
from email.mime.text import MIMEText

# Define email sender and receiver
email_sender = 'weirdunboxings01@gmail.com'
email_password = 'woasifczvxpvplnh'
email_receiver = 'write-email-receiver-here'
app = Flask(__name__)
app.secret_key = 'chupmg'
import sqlalchemy as sa
engine = sa.create_engine('mssql+pyodbc://{username}:{password}@{server}:{port}/{database}?driver={driver}'.format(
    username='sa',
    password='tap2024',
    server=r'APINP-ELPT47172\SQLEXPRESS',
    port='1433',
    database='anshu',
    driver='ODBC Driver 17 for SQL server'
))
connection = engine.connect()
from sqlalchemy import Table, Column, Integer, String, MetaData,insert,select,ForeignKey,DateTime,sql,update,TIMESTAMP,func,or_
meta = MetaData()
accounts = Table(
   'accounts', meta,  
   Column('address', String), 
   Column('first_name',String),
   Column('last_name', String), 
   Column('balance',Integer),
   Column('type',String),
   Column('account_no',String),
   Column('password',String),
   Column('email',String),
   Column('phone_no',String)
)
transactions = Table(
    'transactions',meta,
    Column('from_user',String,ForeignKey('accounts.username')),
    Column('to_user',String,ForeignKey('accounts.username')),
    Column('amount',Integer),
    Column('time',DateTime,server_default=sql.func.now())
)
admins = Table(
    'admins',meta,
    Column('id',String),
    Column('password',String)
)
logs = Table(
    'logs',meta,
    Column('time',DateTime,server_default=sql.func.now()),
    Column('information',String),
    Column('type',String)
)

def login_required(view_func):
    def func():
        if 'username' in session:
            username = session['username']
            return view_func(username)
        return "failed , username not in session"
    return func
# meta.create_all(engine)
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
@app.route("/")
def hello():
    if 'username' in session:
        return redirect('/dashboard')
    return render_template("index.html")
# @app.route("/dashboard")
# @login_required

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=='POST':
        select_statement = select(accounts).where(accounts.c.email==request.form['username'],accounts.c.password==request.form['password'])
        result = connection.execute(select_statement)
        if result is not None:
            session['username']=str(request.form['username'])
            print(session.keys())
            # print(session['username'])
            session.modified = True
            print(id(session))
            return redirect('/dashboard')
    return render_template('login.html')
@app.route("/logout",endpoint='logout')
@login_required
def logout(username):
    session.pop('username')
    return redirect('/')
@app.route('/admin_logout')
def admin_logout():
    if 'admin' in session:
        session.pop('admin')
    return redirect('/')
    
@app.route("/update_password",methods=['GET','POST'],endpoint='update_password')
def update_password():
    if request.method == 'POST':
        try:
            update_statement = update(accounts).where(accounts.c.email==request.form['username']).values(password=request.form['password'])
            connection.execute(update_statement)
            connection.commit()
            return "updation successful"
        except Exception as e:
            return "user not present . First create account"
        return "password updated"
    return render_template("update_password.html")
@app.route("/update_credentials",methods=['GET','POST'],endpoint='update_creds')
@login_required
def update_credentials(username):
    statement = select(accounts).where(accounts.c.email==username)
    data = connection.execute(statement).first()
    temp = data
    data = dict()
    data['address'] = temp[0]
    data['first_name'] = temp[1]
    data['last_name'] = temp[2]
    data['balance'] = temp[3]
    data['account_no'] = temp[5]
    data['password'] = temp[6]
    data['email'] = temp[7]
    data['phone_no'] = temp[8]
    if request.method=='POST':
        stt = update(accounts).where(accounts.c.email==username).values(balance=request.form['balance'],first_name=request.form['first_name'],
                                       last_name=request.form['last_name'],email=request.form['email'],password=request.form['password'],
                                        phone_no=request.form['phone_no'])
        connection.execute(stt)
        connection.commit()
        session['username']=request.form['email']
        return redirect('/dashboard')
    return render_template("update.html",data=data)
@app.route("/dashboard",endpoint='hhheheh')
@login_required
def dashboard(username):
    data = dict()
    account_no = connection.execute(select(accounts.c.account_no).where(accounts.c.email==username)).first()[0]
    query = select(transactions).where(or_(transactions.c.from_user== account_no, transactions.c.to_user==account_no) ).order_by(transactions.c.time).limit(5)
    data['transactions'] = connection.execute(query).fetchall()
    first_name = connection.execute(select(accounts).where(accounts.c.email==username)).first()[1]
    last_name = connection.execute(select(accounts).where(accounts.c.email==username)).first()[2]
    data['name'] = first_name+" "+last_name
    data['username'] = account_no
    data['balance'] = connection.execute(select(accounts.c.balance).where(accounts.c.email==username)).fetchone()
    return render_template("dashboard.html",data=data)
@app.route("/transaction",methods=['GET','POST'])
@login_required
def transaction(username):
    if request.method=='POST':
        try:
            account_no = connection.execute(select(accounts.c.account_no).where(accounts.c.email==username)).first()[0]
            insert_statement = insert(transactions).values({'from_user':account_no,'to_user':request.form['account_no'],'amount':request.form['amount']})
            connection.execute(insert_statement)
            connection.commit()
            update_statement1 = update(accounts).where(accounts.c.account_no==account_no).values(balance=accounts.c.balance-request.form['amount'])
            update_statement2 = update(accounts).where(accounts.c.account_no==request.form['account_no']).values(balance=accounts.c.balance+request.form['amount'])
            connection.execute(update_statement1)
            connection.execute(update_statement2)
            connection.commit()
            subject = "transaction status"
            msg = f'Your transaction from {account_no} to {request.form['account_no']} for amount {request.form['amount']} is successful'
        except Exception as e:
            temp = insert(logs).values(information='transaction failed',type='L1')
            connection.execute(temp)
            connection.commit()
            return "<h1>some error ouccured</h1>"
        sts = select(accounts.c.email).where(accounts.c.account_no==account_no)
        try:
            sendmail(subject,msg,connection.execute(sts).first()[0])
        except Exception as e:
            sst = insert(logs).values(information='sending email failed',type='L1')
            connection.execute(sst)
            connection.commit()
        return "<h1>transaction succesfull</h1>"
    return render_template("transaction.html")
@app.route("/new_account",methods=['GET','POST'])
def account_opening():
    form = AccountOpeningForm(request.form)
    if request.method == 'POST':
        digits = "0123456789"
        account_no = "".join(random.choice(digits) for _ in range(14))
        try:
            insert_statment = insert(accounts).values(address=form.address.data,first_name=form.first_name.data,last_name=form.last_name.data,balance=form.balance.data,type=form.type_account.data,
                                                    account_no=account_no,password=form.password.data,email=form.email.data,phone_no=form.phone_no.data)
            connection.execute(insert_statment)
            connection.commit()
            return redirect('/dashboard')
        except Exception as e:
            sst = insert(logs).values(information='account opening failed',type='L2')
            connection.execute(sst)
            connection.commit()
            return render_template("new_account.html",form=form,message="account_opening_failed")
    return render_template('new_account.html', form=form)
@app.route("/admin",methods=['GET','POST'])
def admin_pannel():
    if 'admin' in session:
        data = dict()
        data['transactions'] = connection.execute(select(transactions)).fetchall()
        data['accounts'] = connection.execute(select(accounts)).fetchall()
        data['logs'] = connection.execute(select(logs)).fetchall()
        return render_template("admin.html",data=data)
    else:
        if request.method=='POST':
            sst = select(admins).where(admins.c.id==request.form['id'])
            hehe = connection.execute(sst)
            if hehe is not None:
                session['admin'] = request.form['id']
                return redirect("/admin")
        return render_template("admin.html")
                