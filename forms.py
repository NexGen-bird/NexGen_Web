from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, TextAreaField, IntegerField, IntegerRangeField, FloatField, BooleanField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Email, Length, InputRequired, NumberRange
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
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=13)])
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
    
    submit = SubmitField('Submit')

class TransactionForm(FlaskForm):
    transaction_type = SelectField('Transaction Type', choices=[('General', 'General'), ('Admission', 'Admission'), ('Investment', 'Investment')], validators=[DataRequired()])
    transaction_date = DateField('Transaction Date', default=date.today, validators=[DataRequired()])
    plan = SelectField('Plan', choices=[
        (2, 'Monthly'), (3, 'Quarterly'), 
        (4, 'Half Yearly'), (5, 'Yearly'), 
        (1, 'Day'), (6, 'Weekend')
    ])
    shifts = MultiCheckboxField('Shifts', choices=[
        (1, '6am - 12pm'), (2, '12pm - 6pm'),
        (3, '6pm - 12am'), (4, '12am - 6am')
    ],default=['6am-12pm'],validate_choice=[])
    start_date = DateField('Start Date',default=date.today)
    end_date = DateField('End Date')
    locker_number = IntegerRangeField('Locker Number', default=0,validators=[InputRequired(), NumberRange(min=0, max=6)],  # backend validation
        render_kw={"type": "number", "min": 0, "max": 6})
    txn_made_by = StringField('txn made by')
    txn_made_to = StringField('txn made to')
    amount = IntegerField('Amount', validators=[DataRequired()])
    txn_type = SelectField('Txn Type', choices=[('IN', 'IN'), ('OUT', 'OUT')])
    payment_method = SelectField('Payment Method', choices=[
        ('Cash', 'Cash'), ('UPI', 'UPI'), ('Partial', 'Partial')
    ], validators=[DataRequired()])
    cash_amount = IntegerField('Cash Amount', default=0)
    upi_amount = IntegerField('UPI Amount', default=0)
    description = TextAreaField('Description')
    submit = SubmitField('Save Transaction')
