from wtforms import Form,BooleanField,StringField,PasswordField,validators,SelectField,FloatField,EmailField

class AccountOpeningForm(Form):
    # username = StringField('Username', [validators.Length(min=4, max=25)])
    # email = StringField('Email Address', [validators.Length(min=6, max=35)])
    # password = PasswordField('New Password', [
    #     validators.DataRequired(),
    #     validators.EqualTo('confirm', message='Passwords must match')
    # ])
    # confirm = PasswordField('Repeat Password')
    # accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])
    first_name = StringField('first_name')
    last_name = StringField('last_name')
    type_account = SelectField('account_type',choices=['saving','current'])
    address = StringField('address')
    balance = FloatField('balance')
    # username = StringField('username')
    password = PasswordField('password')
    email = EmailField('email')
    phone_no = StringField('phone_no')
