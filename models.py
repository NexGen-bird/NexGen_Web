from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_number = db.Column(db.String(15), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    education_details = db.Column(db.Text)
    study_option = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text, nullable=False)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='customer', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)  # Nullable for investment transactions
    transaction_type = db.Column(db.String(20), nullable=False)  # 'admission', 'general', 'investment'
    transaction_date = db.Column(db.Date, nullable=False)
    plan = db.Column(db.String(20))  # Monthly, Quarterly, etc. (nullable for investment)
    shifts = db.Column(db.Text)  # JSON string of selected shifts
    start_date = db.Column(db.Date)  # Nullable for investment
    end_date = db.Column(db.Date)  # Nullable for investment
    locker_number = db.Column(db.String(10))
    amount = db.Column(db.Float, nullable=False)
    txn_type = db.Column(db.String(3))  # 'IN' or 'OUT'
    payment_method = db.Column(db.String(20), nullable=False)
    cash_amount = db.Column(db.Float, default=0)
    upi_amount = db.Column(db.Float, default=0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    partner_name = db.Column(db.String(100), nullable=False)
    investment_amount = db.Column(db.Float, nullable=False)
    investment_date = db.Column(db.Date, nullable=False)
    returns = db.Column(db.Float, default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Locker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    locker_number = db.Column(db.String(10), unique=True, nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    assigned_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    customer = db.relationship('Customer', backref='assigned_locker')
