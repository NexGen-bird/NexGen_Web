from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, TextAreaField, FloatField, BooleanField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Email, Length
from datetime import date

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

class AdmissionForm(FlaskForm):
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    education_details = TextAreaField('Education Details')
    study_option = SelectField('Study Option', choices=[
        ('CA/CS', 'CA/CS'), ('JEE', 'JEE'), ('HSC', 'HSC'), 
        ('Police Bharti', 'Police Bharti'), ('MPSC', 'MPSC'), ('UPSC', 'UPSC'), 
        ('NEET', 'NEET'), ('Medical Examinations', 'Medical Examinations'), 
        ('Banking', 'Banking'), ('Law', 'Law'), ('Others', 'Others')
    ], validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])
    note = TextAreaField('Note')
    submit = SubmitField('Submit')

class TransactionForm(FlaskForm):
    transaction_type = SelectField('Transaction Type', choices=[('general', 'General'), ('admission', 'Admission'), ('investment', 'Investment')], validators=[DataRequired()])
    transaction_date = DateField('Transaction Date', default=date.today, validators=[DataRequired()])
    plan = SelectField('Plan', choices=[
        ('Monthly', 'Monthly'), ('Quarterly', 'Quarterly'), 
        ('Half Yearly', 'Half Yearly'), ('Yearly', 'Yearly'), 
        ('Day', 'Day'), ('Weekend', 'Weekend')
    ])
    shifts = MultiCheckboxField('Shifts', choices=[
        ('6am-12pm', '6am - 12pm'), ('12pm-6pm', '12pm - 6pm'),
        ('6pm-12am', '6pm - 12am'), ('12am-6am', '12am - 6am')
    ])
    start_date = DateField('Start Date')
    end_date = DateField('End Date')
    locker_number = StringField('Locker Number')
    amount = FloatField('Amount', validators=[DataRequired()])
    txn_type = SelectField('Txn Type', choices=[('IN', 'IN'), ('OUT', 'OUT')])
    payment_method = SelectField('Payment Method', choices=[
        ('Cash', 'Cash'), ('UPI', 'UPI'), ('Partial', 'Partial')
    ], validators=[DataRequired()])
    cash_amount = FloatField('Cash Amount', default=0)
    upi_amount = FloatField('UPI Amount', default=0)
    description = TextAreaField('Description')
    submit = SubmitField('Save Transaction')
