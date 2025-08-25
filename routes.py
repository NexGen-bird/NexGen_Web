from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db
from models import User, Customer, Transaction, Investment
from forms import LoginForm, ForgotPasswordForm, AdmissionForm, TransactionForm
from utils import create_whatsapp_url, get_whatsapp_receipt_message, get_whatsapp_expiry_reminder, calculate_age, format_currency
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract
import json

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # In a real application, you would send an email here
            flash('Password reset link sent to your email!', 'info')
        else:
            flash('No account found with that email address.', 'warning')
        return redirect(url_for('login'))
    return render_template('forgot_password.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Calculate dashboard metrics
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Active members (customers with active subscriptions)
    active_members = db.session.query(Customer).join(Transaction).filter(
        Transaction.end_date >= date.today()
    ).distinct().count()
    
    # Expired subscriptions
    expired_subscriptions = db.session.query(Customer).join(Transaction).filter(
        Transaction.end_date < date.today()
    ).distinct().count()
    
    # Current month transactions
    current_month_transactions = Transaction.query.filter(
        extract('month', Transaction.transaction_date) == current_month,
        extract('year', Transaction.transaction_date) == current_year
    ).all()
    
    current_month_pl = sum(t.final_amount for t in current_month_transactions)
    
    # Net P&L (all time)
    net_pl = sum(t.final_amount for t in Transaction.query.all())
    
    # Total collection
    total_collection = net_pl
    
    # Total expenses (placeholder - would come from expense tracking)
    total_expenses = 0  # This would be calculated from an expenses table
    
    # Shift data (placeholder - would be calculated from actual shift assignments)
    shift_data = {
        '1st Shift': 25,
        '2nd Shift': 30,
        '3rd Shift': 20,
        '4th Shift': 15,
        'Weekend': 35
    }
    
    # Expiring subscriptions (next 7 days)
    expiring_date = date.today() + timedelta(days=7)
    expiring_subscriptions = db.session.query(Customer, Transaction).join(Transaction).filter(
        Transaction.end_date.between(date.today(), expiring_date)
    ).all()
    
    metrics = {
        'active_members': active_members,
        'expired_subscriptions': expired_subscriptions,
        'current_month_pl': current_month_pl,
        'net_pl': net_pl,
        'total_collection': total_collection,
        'total_expenses': total_expenses
    }
    
    return render_template('dashboard.html', 
                         metrics=metrics, 
                         shift_data=shift_data,
                         expiring_subscriptions=expiring_subscriptions,
                         create_whatsapp_url=create_whatsapp_url,
                         get_whatsapp_expiry_reminder=get_whatsapp_expiry_reminder,
                         format_currency=format_currency)

@app.route('/admission', methods=['GET', 'POST'])
def admission():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    form = AdmissionForm()
    if form.validate_on_submit():
        age = calculate_age(form.date_of_birth.data)
        
        customer = Customer()
        customer.contact_number = form.contact_number.data
        customer.full_name = form.full_name.data
        customer.date_of_birth = form.date_of_birth.data
        customer.age = age
        customer.gender = form.gender.data
        customer.email = form.email.data
        customer.education_details = form.education_details.data
        customer.study_option = form.study_option.data
        customer.address = form.address.data
        customer.note = form.note.data
        
        db.session.add(customer)
        db.session.commit()
        
        flash('Admission form submitted successfully!', 'success')
        return redirect(url_for('add_transaction', customer_id=customer.id, transaction_type='admission'))
    
    return render_template('admission.html', form=form)

@app.route('/add-transaction')
@app.route('/add-transaction/<int:customer_id>')
def add_transaction(customer_id=None):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    form = TransactionForm()
    customers = Customer.query.all()
    
    # If coming from admission page, pre-select customer and transaction type
    selected_customer = None
    if customer_id:
        selected_customer = Customer.query.get(customer_id)
        form.transaction_type.data = request.args.get('transaction_type', 'admission')
    
    if request.method == 'POST' and form.validate_on_submit():
        # Calculate final amount
        amount = form.amount.data or 0
        discount = form.discount.data or 0
        final_amount = amount - discount
        
        transaction = Transaction()
        transaction.customer_id = customer_id or request.form.get('customer_id')
        transaction.transaction_type = form.transaction_type.data
        transaction.transaction_date = form.transaction_date.data
        transaction.plan = form.plan.data
        transaction.shifts = json.dumps(form.shifts.data)
        transaction.start_date = form.start_date.data
        transaction.end_date = form.end_date.data
        transaction.is_regular = form.is_regular.data
        transaction.locker_number = form.locker_number.data
        transaction.amount = amount
        transaction.discount = discount
        transaction.final_amount = final_amount
        transaction.payment_method = form.payment_method.data
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('receipt', transaction_id=transaction.id))
    
    return render_template('add_transaction.html', 
                         form=form, 
                         customers=customers, 
                         selected_customer=selected_customer)

@app.route('/transactions')
def transactions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('transactions.html', transactions=transactions)

@app.route('/customers')
def customers():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    page = request.args.get('page', 1, type=int)
    
    # Get all customers first, then add transaction info
    customers_data = []
    all_customers = Customer.query.all()
    
    for customer in all_customers:
        latest_transaction = Transaction.query.filter_by(customer_id=customer.id).order_by(Transaction.end_date.desc()).first()
        latest_expiry = latest_transaction.end_date if latest_transaction else None
        transaction_count = Transaction.query.filter_by(customer_id=customer.id).count()
        customers_data.append((customer, latest_expiry, transaction_count))
    
    # Simple pagination implementation
    per_page = 20
    total = len(customers_data)
    start = (page - 1) * per_page
    end = start + per_page
    items = customers_data[start:end]
    
    # Create pagination object manually
    class Pagination:
        def __init__(self, page, per_page, total, items):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.items = items
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None
            
        def iter_pages(self, left_edge=2, right_edge=2, left_current=2, right_current=3):
            last = self.pages
            for num in range(1, last + 1):
                if num <= left_edge or \
                   (self.page - left_current - 1 < num < self.page + right_current) or \
                   num > last - right_edge:
                    yield num
    
    customers = Pagination(page, per_page, total, items)
    
    return render_template('customers.html', 
                         customers=customers,
                         create_whatsapp_url=create_whatsapp_url,
                         get_whatsapp_expiry_reminder=get_whatsapp_expiry_reminder,
                         date=date)

@app.route('/investment-summary')
def investment_summary():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    investments = Investment.query.all()
    
    # Calculate totals
    total_investment = sum(inv.investment_amount for inv in investments)
    total_returns = sum(inv.returns for inv in investments)
    net_profit = total_returns - total_investment
    
    summary = {
        'total_investment': total_investment,
        'total_returns': total_returns,
        'net_profit': net_profit
    }
    
    return render_template('investment_summary.html', 
                         investments=investments, 
                         summary=summary,
                         format_currency=format_currency)

@app.route('/receipt/<int:transaction_id>')
def receipt(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    transaction = Transaction.query.get_or_404(transaction_id)
    customer = transaction.customer
    
    # Generate WhatsApp receipt message
    whatsapp_message = get_whatsapp_receipt_message(
        customer.full_name,
        transaction.final_amount,
        transaction.plan,
        transaction.start_date,
        transaction.end_date
    )
    
    whatsapp_url = create_whatsapp_url(customer.contact_number, whatsapp_message)
    
    return render_template('receipt.html', 
                         transaction=transaction, 
                         customer=customer,
                         whatsapp_url=whatsapp_url,
                         format_currency=format_currency)

# API endpoint for dashboard charts
@app.route('/api/dashboard-data')
def dashboard_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Last 3 months P&L data
    months = []
    revenue_data = []
    expense_data = []
    
    for i in range(3):
        month_date = datetime.now() - timedelta(days=30*i)
        month_name = month_date.strftime('%B')
        months.insert(0, month_name)
        
        # Calculate revenue for the month
        month_transactions = Transaction.query.filter(
            extract('month', Transaction.transaction_date) == month_date.month,
            extract('year', Transaction.transaction_date) == month_date.year
        ).all()
        
        revenue = sum(t.final_amount for t in month_transactions)
        revenue_data.insert(0, revenue)
        
        # Placeholder for expenses
        expense_data.insert(0, revenue * 0.3)  # Assuming 30% expenses
    
    # Admission summary (last 3 months)
    admission_data = []
    for i in range(3):
        month_date = datetime.now() - timedelta(days=30*i)
        admissions = Transaction.query.filter(
            Transaction.transaction_type == 'admission',
            extract('month', Transaction.transaction_date) == month_date.month,
            extract('year', Transaction.transaction_date) == month_date.year
        ).count()
        admission_data.insert(0, admissions)
    
    return jsonify({
        'months': months,
        'revenue_data': revenue_data,
        'expense_data': expense_data,
        'admission_data': admission_data
    })

# Create default admin user
def create_admin():
    try:
        if not User.query.filter_by(email='admin@nexgen.com').first():
            admin = User()
            admin.email = 'admin@nexgen.com'
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        # Tables might not exist yet, will be created later
