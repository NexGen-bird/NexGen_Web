from flask import render_template, request, redirect, url_for, flash, session, jsonify, render_template_string
from app import app, db
from models import User, Customer, Transaction, Investment, Locker
from forms import LoginForm, ForgotPasswordForm, AdmissionForm, TransactionForm
from utils import create_whatsapp_url, get_whatsapp_receipt_message,get_receipt_link_msg, get_whatsapp_expiry_reminder, calculate_age, format_currency, format_currency_denomination
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract
import json
import threading
import concurrent.futures
from functools import partial
from utilities.supabase_db import *
from utilities.apputils import *

from supabase_lib.supabase_auth import *

app.jinja_env.filters["bgcolor"] = get_background_color
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # user = User.query.filter_by(email=form.email.data).first()
        user = login_with_email_password(form.email.data,form.password.data)
        # if user and user.check_password(form.password.data):
        if user:
            session['user_id'] = user.user.id
            session['email'] = user.user.email
            # session["access_token"] = user.session.access_token
            # session["refresh_token"] = user.session.refresh_token
            session['userName'] = "Abhijit Shinde" if "shinde" in user.user.email else "Jayesh Thakre" if "thakre" in user.user.email else "NexGen" 
            print("Response ----> ",user,"------>End<-------")
            flash('Logged in successfully!', 'success')
            
            # flash(session.get("email"),'success')
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
def logoutuser():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'info')
    session.pop('admission_form_details', None)
    session.pop('transaction_type', None)
    logout()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    api_results = {}
    shifts = {"morning": "45", "afternoon": "45", "evening": "45","night":"45","weekend":"20"}

    weekend_ppl_count = """
                        SELECT 20-COUNT(DISTINCT customerid) as count
                        FROM subscription
                        WHERE isactive = 1 and planstartdate <= current_date and planduerationid = 6
                        """
    shiftwiseactivecount = """
                            SELECT CONCAT('Shift',shiftid, ':', 45-COUNT(DISTINCT seatid)) as count
                            FROM subscription
                            WHERE isactive = 1 and planstartdate <= current_date and planduerationid != 6-- Filter for active subscriptions
                            GROUP BY shiftid
                            """
    collection_query = """SELECT 
SUM(CASE WHEN transaction_type = 'IN' THEN amount ELSE 0 END) AS total_revenue,
SUM(CASE WHEN transaction_type = 'OUT' THEN amount ELSE 0 END) AS total_expenses
    FROM "Transactions"
    """
    active_members_query = """select count(distinct customerid)
                            from subscription
                            where isactive=1
                            """
    exp_members_query = """SELECT DISTINCT ON (c.id) 
                                c.id, 
                                c.name,
                                c.phone_number, 
                                p.planstartdate,
                                p.planexpirydate,
                                c.profile_image,
                                c.address,
                                (select plandueration from plandueration where id in(p.planduerationid)) as "plan"
                            FROM "Customers" c
                            INNER JOIN "subscription"  p ON c.id = p.customerid
                            where p.planexpirydate >= current_date
                            """
    expired_count = """
                    select count(distinct customerid)
                    from subscription
                    where isactive=0 and customerid not in (select distinct customerid
                    from subscription
                    where isactive=1)
                    """
    month_start,month_end = apputils.get_current_period_range()
    print("This is dates ---> ",month_start,month_end)
    api_tasks = {
        "shiftcount": partial(run_sql,shiftwiseactivecount),
        "weekendcount": partial(run_sql,weekend_ppl_count),
        "collection": partial(run_sql,collection_query),
        "active_members": partial(run_sql,active_members_query),
        "pnl_amount": partial(get_net_profit,month_start,month_end),
        "expired_count": partial(run_sql,expired_count),
        "expiring_members": partial(run_sql,exp_members_query),
    }

    results = {}
    #login_with_email_password("abhijit.shinde@test.com","india@123")
    # with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    #     future_to_key = {
    #         executor.submit(func): key for key, func in api_tasks.items()
    #     }

    #     for future in concurrent.futures.as_completed(future_to_key):
    #         key = future_to_key[future]
    #         try:
    #             results[key] = future.result()
    #         except Exception as e:
    #             results[key] = f"Error: {str(e)}"

    # New Logic ------
    for key, func in api_tasks.items():
        try:
            results[key] = func()
        except Exception as e:
            results[key] = f"Error: {str(e)}"
    api_results = results
    # Schedule UI update only if still active
    if api_results:
        _active_members = api_results['active_members']
        shiftcount = api_results['shiftcount']
        weekendcount = api_results['weekendcount']
        collection = api_results['collection']
        pnl_amount = api_results['pnl_amount']
        _expired_count = api_results['expired_count']
        expiring_members = api_results['expiring_members'] 


        dash_active_members = str("0" if _active_members[0]['count']==None else _active_members[0]['count'])
        
        dash_pnl_amount = str(0 if pnl_amount==None else apputils.format_number(float(pnl_amount)))
        dash_pnl_amount_absolute = str("{} {}".format("₹",format_inr(0 if pnl_amount==None else pnl_amount)))
        
        if weekendcount:# weekend batch available seats
            print("Weekend batch --> ",weekendcount[0]['count'])
            shifts["weekend"] = str(weekendcount[0]['count'])
        
        # Set Shift count details
        
        if shiftcount:# 1st, 2nd, 3rd, 4th shift availble seats
            # Mapping shift names to dictionary keys
            shift_mapping = {
                "Shift1": "morning",
                "Shift2": "afternoon",
                "Shift3": "evening",
                "Shift4": "night"
            }

            # Update shifts from shiftcount
            for x in shiftcount:
                shift, count = x['count'].split(":")
                if shift in shift_mapping:
                    shifts[shift_mapping[shift]] = count
        
        if collection:
            dash_collection_amount = str("0" if collection[0]['total_revenue']==None else "{}{}".format("₹", format_number(float(collection[0]["total_revenue"]))))
            dash_collection_amount_absolute = str("0" if collection[0]['total_revenue']==None else "{} {}".format("₹", format_inr(collection[0]["total_revenue"])))
            dash_expense_amount = str("0" if collection[0]['total_expenses']==None else "{}{}".format("₹",format_number(float(collection[0]["total_expenses"]))))
            dash_expense_amount_absolute = str("0" if collection[0]['total_expenses']==None else "{} {}".format("₹",format_inr(collection[0]["total_expenses"])))
            dash_net_pnl ="{}{}".format("₹", format_number(float(int(0 if collection[0]['total_revenue']==None else collection[0]['total_revenue']) - int(0 if collection[0]['total_expenses']==None else collection[0]['total_expenses']))))        
            dash_net_pnl_absolute ="{} {}".format("₹", format_inr(int(0 if collection[0]['total_revenue']==None else collection[0]['total_revenue']) - int(0 if collection[0]['total_expenses']==None else collection[0]['total_expenses'])))      

        dash_expired_count = str("0" if _expired_count[0]['count']==None else _expired_count[0]['count'])     

        if expiring_members:
            sorted_expiring_subscriptions_data = sorted(expiring_members, key=lambda x: datetime.strptime(x['planexpirydate'], "%Y-%m-%d"), reverse=False)
            # for x in sorted_data:
                # self.expCard(id=x['id'],name=x['name'],expdate=x['planexpirydate'],phone=x['phone_number'],img=x['profile_image'])
        else:
            print("No Expiring subciptions..")
    # -------------->OLD SECTION<----------------
    # Calculate dashboard metrics

    # Available lockers
    total_lockers = 6  # Total number of lockers
    occupied_lockers = 4
    available_lockers = total_lockers - occupied_lockers
    
    metrics = {
        'active_members': dash_active_members,
        'expired_subscriptions': dash_expired_count,
        'current_month_pl': dash_pnl_amount,
        'net_pl': dash_net_pnl,
        'total_collection': dash_collection_amount,
        'total_expenses': dash_expense_amount,
        'dash_collection_amount_absolute': dash_collection_amount_absolute,
        'dash_expense_amount_absolute':dash_expense_amount_absolute,
        'dash_net_pnl_absolute': dash_net_pnl_absolute,
        'dash_pnl_amount_absolute': dash_pnl_amount_absolute
    }
    
    return render_template('dashboard.html', 
                         metrics=metrics, 
                         shifts=shifts,
                         available_lockers=available_lockers,
                         expiring_subscriptions=sorted_expiring_subscriptions_data,
                         create_whatsapp_url=create_whatsapp_url,
                         get_whatsapp_expiry_reminder=get_whatsapp_expiry_reminder)

@app.route("/api/customer/<customer_id>")
def get_customer(customer_id):
    # just dummy data for testing
    print("This is customer data --> ",customer_id)
    customer_info = f"""
SELECT DISTINCT ON (c.id) 
c.id, 
c.name,
c.phone_number, 
c.email,
p.planstartdate,
p.planexpirydate,
c.profile_image,
c.address,
c.dob,
c.education,
(select plandueration from plandueration where id in(p.planduerationid)) as "plan"
FROM "Customers" c
INNER JOIN "subscription"  p ON c.id = p.customerid
where p.planexpirydate >= current_date and c.id = '{customer_id}'
"""
    cust_data = run_sql(customer_info)
    print("This is data -- > ",cust_data[0])
    if cust_data:
        customer_data = {
            "id": cust_data[0]['id'],
            "name": cust_data[0]['name'],
            "phone_number": cust_data[0]['phone_number'],
            "email": cust_data[0]['email'],
            "plan": f"Premium {cust_data[0]['plan']}",
            "planexpirydate": date_format(cust_data[0]['planexpirydate']),
            "address": cust_data[0]['address'],
            "dob": cust_data[0]['dob'],
            "education": cust_data[0]['education'],
            "profile_image": "/static/images/male.jpg"
        }
    else:
        customer_data= {}
    return jsonify(customer_data)

@app.route("/autocomplete/txnnames")
def autocomplete_txnnames():
    # Fetch all names once
    customer_data = run_sql("""SELECT name,phone_number 
                            FROM "Customers"
                            """)
    names = customer_data  # should return a list like ["Alice", "Bob", "Charlie"]
    # print(names)
    print(customer_data)
    if names:
        q = request.args.get("q", "").strip().lower()
        results = []

        if q:
            # Filter names containing query (case-insensitive)
            results = [f"{name['name']} - {name['phone_number']}" for name in names if q in name['name'].lower()]
            print(f"Serch--> {results}")
        # Limit to 10 results
        results = results[:10]
    else:
        flash("No Contacts details found..","danger")
        results = None
    return jsonify(results)

@app.route("/autocomplete/names")
def autocomplete_names():
    # Fetch all names once
    names = get_all_customers_names()  # should return a list like ["Alice", "Bob", "Charlie"]
    if names:
        q = request.args.get("q", "").strip().lower()
        results = []

        if q:
            # Filter names containing query (case-insensitive)
            results = [name for name in names if q in name.lower()]
        # Limit to 10 results
        results = results[:10]
    else:
        flash("No Contacts details found..","danger")
        results = None
    return jsonify(results)

@app.route("/autocomplete/contacts")
def autocomplete_contacts():
    # Fetch all names once
    names = get_all_customers_contact()  # should return a list like ["9930253216", "1234567890", "9087654321"]
    if names:
        q = request.args.get("q", "").strip()
        results = []

        if q:
            # Filter names containing query (case-insensitive)
            results = [name for name in names if q in name]
        # Limit to 10 results
        results = results[:10]
    else:
        flash("No Contacts details found..","danger")
        results = None
    return jsonify(results)


@app.route("/get_student_details", methods=["GET"])
def get_student_details():
    # get_customers_details("name",text_item)
    contact = request.args.get("contact")
    name = request.args.get("name")
    details = None

    if contact:
        result = get_customers_details("phone_number",contact)
        if result:
            details = result[0]
        else:
            flash("Please Re-Login")
    elif name:
        result = get_customers_details("name",name)
        if result:
            details = result[0]
        else:
            flash("Please Re-Login")

    # Placeholder response (replace with Supabase DB call)
    if details:
        
        return {
            "full_name": details["name"],
            "contact_number": details["phone_number"],
            "dob": details["dob"],
            "gender": details["gender"],
            "email": details["email"],
            "study_option": details["joining_for"],
            "education_details": details["education"],
            "address": details["address"],
            "profile_img":details["profile_image"]
        }
    return {}

@app.route('/admission', methods=['GET', 'POST'])
def admission():
    #login_with_email_password("abhijit.shinde@test.com","india@123")

    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    form = AdmissionForm()
    if form.validate_on_submit():
        print("Admission form submission method...")
        age = calculate_age(form.date_of_birth.data)
        form_data = {
                "customer_name": form.full_name.data,
                "customer_dob": form.date_of_birth.data.strftime('%Y-%m-%d'),
                "customer_gender": form.gender.data,
                "customer_phone_number": form.contact_number.data,
                "customer_email": form.email.data,
                "customer_education": form.education_details.data,
                "customer_joining_for": form.study_option.data,
                "customer_address": form.address.data,
                "customer_profile_image": "assets/img/female.jpg" if form.gender.data == "Female" else "assets/img/male.jpg",
                # "customer_profile_image": self.profile_image.strip(),
            }
        
        # customer = {"contact_number":"","full_name":"","date_of_birth":"","age":"","gender":"","email":"","education_details":"","study_option":"","address":""}
        # customer['contact_number'] = form.contact_number.data
        # customer['full_name'] = form.full_name.data
        # customer['date_of_birth'] = form.date_of_birth.data.strftime('%Y-%m-%d')
        # customer['age'] = age
        # customer['gender'] = form.gender.data
        # customer['email'] = form.email.data
        # customer['education_details'] = form.education_details.data
        # customer['study_option'] = form.study_option.data
        # customer['address'] = form.address.data
        
        
        # db.session.add(customer)
        # db.session.commit()
        print("Form Data - > ",form_data)
        session['admission_form_details'] = form_data
        flash(form_data,'success')
        
        flash('Admission form submitted successfully!', 'success')
        return redirect(url_for('add_transaction', customer_details=None, transaction_type='Admission'))
    
    return render_template('admission.html', form=form)

@app.route('/add-transaction', methods=["GET", "POST"])
@app.route('/add-transaction/<customer_details>', methods=["GET", "POST"])
def add_transaction(customer_details=None):
    login_with_email_password("abhijit.shinde@test.com","india@123")
    flash(f"Session data --> {session.get('admission_form_details')}",'success')
    if 'user_id' not in session:
        return redirect(url_for('login'))
    customer_details = session.get('admission_form_details')
    number = "8108236131"
    form = TransactionForm()
    customers = (run_sql(f"""SELECT name,phone_number From "Customers" """))
    
    # If coming from admission page, pre-select customer and transaction type
    selected_customer = None
    if customer_details:
        selected_customer_query = run_sql(f"""SELECT name,phone_number From "Customers" where phone_number = '{customer_details['customer_phone_number']}'""")
        selected_customer = {'name':customer_details['customer_name'],'phone_number':customer_details['customer_phone_number']} if selected_customer_query == None else selected_customer_query[0]
        # print("Test -->",selected_customer)
        form.transaction_type.data = request.args.get('transaction_type', 'Admission')
    
    if form.validate_on_submit():
        txn_date = apputils.add_current_time_to_date(form.transaction_date.data.strftime('%Y-%m-%d'))
        # data for admission SP
        plantypeid = 1
        if len(form.shifts.data) >3:
            plantypeid = 5
        elif len(form.shifts.data) >2:
            plantypeid = 3
        elif len(form.shifts.data) ==2:
            plantypeid = 2
        else:
            plantypeid = 1
        admission_form_data = {
                "customer_name": "",
                "customer_dob": "2000-09-28",
                "customer_gender": f"",
                "customer_phone_number": "",
                "customer_email": "",
                "customer_education": "",
                "customer_joining_for": "",
                "customer_address": "",
                "customer_profile_image": "assets/img/female.jpg" 
                # "customer_profile_image": self.profile_image.strip(),
            }
        data = {
            "customer_transaction_date": txn_date,
            "customer_transaction_type": form.txn_type.data,
            "customer_amount": form.amount.data or 0,
            "customer_payment_method": form.payment_method.data,
            "customer_description": form.description.data.strip(),
            "customer_transaction_for": form.transaction_type.data.strip(),
            "customer_transaction_made_to": form.txn_made_to.data.strip(),
            "customer_plantypeid": plantypeid,
            "customer_planduerationid": form.plan.data,
            "customer_shiftid": form.shifts.data,  # Pass multiple shift IDs as a list
            "customer_seatid": 1,
            "customer_planstartdate": form.start_date.data.strftime('%Y-%m-%d'),
            "customer_planexpirydate":form.end_date.data.strftime('%Y-%m-%d'),
            "customer_paymenttype": form.payment_method.data,
            "customer_isactive": 1,
            "is_locker": 1 if form.locker_number.data>0 else 0,
            "locker_no": int(form.locker_number.data)
        }
        # flash(f"Transaction form data --> {data}","danger")
        # in case user directly add renewal from Add TXN page by selecting customer name
        if not customer_details and form.transaction_type.data == "Admission":
            # flash(f"customer details --> {customer_details} and {form.transaction_type.data}")
            admission_form_data.update({"customer_phone_number":(request.form.get('full_name').split("-")[1]).strip()})
            # flash(f"selected data ---> {admission_form_data}")
        if form.transaction_type.data != "Admission":
            try:
                res = create_transaction(txn_date=txn_date,
                                transaction_type=form.txn_type.data,
                                amount=int(form.amount.data or 0),
                                txn_made_by=(form.txn_made_by.data.lower()).strip(),
                                payment_method=form.payment_method.data,
                                transaction_for=form.transaction_type.data,
                                description=form.description.data.strip(),
                                transaction_made_to= (form.txn_made_to.data.lower()).strip())
                flash(f"Txn Response --> {res}", 'danger')
                result = res.split(":")[0]
                if result.strip()=="Pass":
                    apputils.snack(color="green",text="Transaction Submitted Successfully!")
                    session.pop('admission_form_details', None)
                    session.pop('transaction_type', None)
                    try:
                        msg = f"""
        *TEST ENTRY FROM WEBSIDE*
        Transaction Type - OUT/Expense
        Transaction Date - {txn_date}
        Transaction Made By - {(form.txn_made_by.data.lower()).strip()}
        Transaction Made To - {(form.txn_made_to.data.lower()).strip()}
        Amount - {form.amount.data}
        Mode of Transaction - {form.payment_method.data}
        Description - {form.description.data.strip()}

        """
                        # create_whatsapp_url(phone_number=number,message=msg)
                    except Exception as e:
                                apputils.snack("red",f"{e}")
            except Exception as e:
                                apputils.snack("red",f"{e}")
        else:
            if customer_details:
                admission_form_data.update(customer_details)
            admission_form_data.update(data)
            # flash(f"Admission Form --> {admission_form_data}")
            res = insert_addmission(admission_form_data)
            # print(f"Admission Result --> {res}")
            result = res.split(":")[0] if res != None else "Fail : Unknown"
            if result.strip()=="Pass":
                apputils.snack(color="green",msg="Admission Submitted Successfully!")
                session.pop('admission_form_details', None)
                session.pop('transaction_type', None)
                try:
                    # user_details = get_customers_details("phone_number",self.addmission_form_data['customer_phone_number'])
                    # user_id = user_details[0]['id']
                    # upload_image(self.addmission_form_data['customer_profile_image'],str(user_id))
                    # profile_url = get_profile_img(user_id)
                    # update_customer(self.addmission_form_data['customer_phone_number'],{"profile_image":f"{profile_url}"})
                    print(f"shifts --> {form.shifts.data}")
                    receipt_data = {
                        "customer_name": str(admission_form_data['customer_name']) if admission_form_data['customer_name']!="" else (request.form.get('full_name').split("-")[0]).strip(),
                        "customer_phone_number": str(admission_form_data['customer_phone_number']),

                        "customer_transaction_date": txn_date,
                        "customer_transaction_id": int((res.split(":")[2]).strip()),
                        "customer_receiptid": str((res.split(":")[4]).strip()),
                        "customer_payment_method": str(form.payment_method.data),
                        "customer_amount": int(form.amount.data),

                        "customer_planstartdate": form.start_date.data.strftime('%Y-%m-%d'),
                        "customer_planexpirydate": form.end_date.data.strftime('%Y-%m-%d'),
                        "customer_shift": str(apputils.get_shift_text(form.shifts.data)),
                        "customer_plantype": str(get_plan_from_id(form.plan.data))
                    }
                    flash(f"receipt data --> {receipt_data}")
                    receipt_res = insert_receipt_data(receipt_data)
                    print(f"receipt Result --> {receipt_res}")
                    if receipt_res:
                        receipt_result = receipt_res.split(":")[0]
                        if receipt_result.strip()=="Pass":
                            apputils.snack(color="green",msg=receipt_res.split(":")[1])
                        else:
                            apputils.snack(color="red",msg=receipt_res.split(":")[1])
                    else:
                        flash("No Receipt result")
                    msg = f"""
    *TEST ENTRY FROM WEBSIDE*
    ID - NG
    Name - {receipt_data['customer_name']}
    phone - {receipt_data['customer_phone_number']}
    Shift - {receipt_data['customer_shift']}
    Locker Number - {admission_form_data['locker_no'] if admission_form_data['is_locker']==1 else "No Locker Taken"}
    Payment mode - {receipt_data['customer_payment_method']}
    Payment Amount- {receipt_data['customer_amount']}
    Payment date - {txn_date}
    Joining Date - {receipt_data['customer_planstartdate']}
    Subscription Expiry date - {receipt_data['customer_planexpirydate']}
                    """
                    # create_whatsapp_url(phone_number=number,message=msg)
                except Exception as e:
                        apputils.snack("red",f"in receipt error --> {e}")
            else:
                apputils.snack(color="red",msg=str(res))
        
        return redirect(url_for('transactions'))
    else:# Clear Session
        print("Form errors:", form.errors)
        # flash("outside Validate Method", "danger")
        # session.pop('admission_form_details', None)
        # session.pop('transaction_type', None)
    
    return render_template('add_transaction.html', 
                         form=form, 
                         customers=customers, 
                         selected_customer=selected_customer)

@app.route('/transactions')
def transactions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    #login_with_email_password("abhijit.shinde@test.com","india@123")
    
    page = request.args.get('page', 1, type=int)
    transactions = get_transactionspagedata()
    # print("This is Test -->", transactions)
    # .paginate(
    #     page=page, per_page=20, error_out=False
    # )
    # Simple pagination implementation
    per_page = 20
    total = len(transactions)
    start = (page - 1) * per_page
    end = start + per_page
    items = transactions[start:end]
    
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
    
    transactions_with_pages = Pagination(page, per_page, total, items)
    return render_template('transactions.html', transactions=transactions,
                           create_whatsapp_url=create_whatsapp_url,
                           get_receipt_link_msg=get_receipt_link_msg)

@app.template_filter("format_date")
def date_format_to(date_):
    return date_format(date_)

@app.template_filter("format_inr")
def format_to_inr(value):
    return format_inr(value if value else 0)

@app.route('/customers')
def customers():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    page = request.args.get('page', 1, type=int)
    
    # Get all customers first, then add transaction info
    customers_data = []
    api_results = {}
    query_customer_list = """
                        SELECT * FROM (
                        SELECT DISTINCT ON (c.id) 
                            c.id, 
                            c.name,
                            c.gender, 
                            c.email, 
                            c.created_at,
                            p.isactive, 
                            p.planstartdate, 
                            p.planexpirydate,
                            c.phone_number,
                            c.profile_image,
                            c.joining_for
                        FROM "Customers" c
                        JOIN "subscription"  p ON c.id = p.customerid::uuid
                        ORDER BY c.id, p.planstartdate DESC
                        ) AS latest_plans
                        ORDER BY planstartdate DESC
                        """
    api_tasks = {
        "customers": partial(run_sql,query_customer_list),
    }

    results = {}
    #login_with_email_password("abhijit.shinde@test.com","india@123")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_key = {
            executor.submit(func): key for key, func in api_tasks.items()
        }

        for future in concurrent.futures.as_completed(future_to_key):
            key = future_to_key[future]
            try:
                results[key] = future.result()
            except Exception as e:
                results[key] = f"Error: {str(e)}"

    api_results = results
    all_customers = api_results['customers']
    print("Customer Listing -- > ",all_customers)
    customers_data = all_customers
    
    
    # Simple pagination implementation
    per_page = 30
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
                         customers=customers_data,
                         create_whatsapp_url=create_whatsapp_url,
                         get_whatsapp_expiry_reminder=get_whatsapp_expiry_reminder,
                         date=date)

@app.route('/investment-summary')
def investment_summary():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    response = get_investmenttransactionspagedata()

    if response:
        transaction_list = response
        
        print("List --> ",transaction_list)
    else:
        transaction_list = None
        print("L3 enter")
        

    jinv_data = get_investment_details('jayesh thakre')
    ainv_data = get_investment_details('abhijit shinde')
    print("jinv_data -- > ",jinv_data)
    print("ainv_data -- > ",ainv_data)
    if jinv_data:
        
        jinvestment = jinv_data[0]['investment'] if jinv_data[0]['investment']!=None else "0"
        jreturns = jinv_data[0]['returns'] if jinv_data[0]['returns']!=None else "0"
        

    else:
        
        print("L3 enter")
        
    if ainv_data:
        ainvestment = ainv_data[0]['investment'] if ainv_data[0]['investment']!=None else "0"
        areturns = ainv_data[0]['returns'] if ainv_data[0]['returns'] !=None else "0"
        

    else:
        
        print("L3 enter")
            
    
    # Get investment transactions
    investment_transactions = transaction_list
    # Calculate summary for single investor view
    Jaya_total_investment = jinvestment
    Jaya_total_returns = jreturns
    Abhi_total_investment = ainvestment
    Abhi_total_returns = areturns
    
    summary = {
        'Abhi_total_investment': Abhi_total_investment,
        'Abhi_total_returns': Abhi_total_returns,
        'Jaya_total_investment': Jaya_total_investment,
        'Jaya_total_returns': Jaya_total_returns
        
    }
    
    return render_template('investment_summary.html', 
                         investment_transactions=investment_transactions, 
                         summary=summary,
                         format_currency=format_currency)

@app.route('/subcriptions')
def subcriptions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    #login_with_email_password("abhijit.shinde@test.com","india@123")
    
    subcriptions = get_subcriptionpagedata()
    print("This is ---> ",subcriptions)
    
    return render_template('subcriptions.html', transactions=subcriptions)

# API endpoint for dashboard charts
@app.route('/api/dashboard-data')
def dashboard_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Last 3 months P&L data
    months_pnl = []
    revenue_data = []
    expense_data = []

    chart_data = get_chart_data()
    if chart_data: 
        for i in chart_data:
            months_pnl.append(i['month'])
            revenue_data.append(i['collection'])
            expense_data.append(i['expense'])
    # ----------->OLD Code <-----------------
    # for i in range(3):
    #     month_date = datetime.now() - timedelta(days=30*i)
    #     month_name = month_date.strftime('%B')
    #     # months.insert(0, month_name)
        
    #     # Calculate revenue for the month
    #     month_transactions = Transaction.query.filter(
    #         extract('month', Transaction.transaction_date) == month_date.month,
    #         extract('year', Transaction.transaction_date) == month_date.year
    #     ).all()
        
    #     revenue = sum(t.final_amount for t in month_transactions)
    #     revenue_data.insert(0, revenue)
        
    #     # Placeholder for expenses
    #     expense_data.insert(0, revenue * 0.3)  # Assuming 30% expenses
    
    # Admission summary (last 3 months)
    months_admission = []
    admission_data = []
    readmission_data = []
    # Admission and reAdmissions chart
    chart_readmission_data = get_admission_chart_data() 
    if chart_readmission_data:
        for i in chart_readmission_data:
            months_admission.append(i['month_label'])
            admission_data.append(i['new_admissions'])
            readmission_data.append(i['readmissions'])
    
    return jsonify({
        'months_pnl': months_pnl,
        'revenue_data':revenue_data,
        'expense_data': expense_data,
        'months_admission': months_admission,
        'admission_data': admission_data,
        'readmission_data': readmission_data
    })

# API endpoint for locker information
@app.route('/api/lockers')
def locker_info():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get all lockers with their assignment info
    lockers = []
    for i in range(1, 51):  # Assuming 50 lockers numbered 1-50
        locker_num = f"L{i:03d}"
        locker = Locker.query.filter_by(locker_number=locker_num).first()
        
        if locker and locker.is_occupied:
            lockers.append({
                'number': locker_num,
                'status': 'Occupied',
                'customer': locker.customer.full_name if locker.customer else 'Unknown',
                'contact': locker.customer.contact_number if locker.customer else '',
                'assigned_date': locker.assigned_date.strftime('%d/%m/%Y') if locker.assigned_date else ''
            })
        else:
            lockers.append({
                'number': locker_num,
                'status': 'Available',
                'customer': '',
                'contact': '',
                'assigned_date': ''
            })
    
    return jsonify({'lockers': lockers})

@app.route("/open_fastapi/<receipt_id>")
def open_fastapi(receipt_id):
    if receipt_id:
        phone_value = run_sql(f"""SELECT phone_number FROM "Customers" where id = (
SELECT reference_id FROM "Transactions" where receipt_id = '{receipt_id}') """)
    phone_number = phone_value  # You can set dynamically
    
    fastapi_url = f"https://nexgeninvoicetracker.onrender.com/receipt/{receipt_id}/verify"
    
    # HTML that opens the FastAPI URL in a new tab with form POST
    html = f"""
    <form id="redirectForm" action="{fastapi_url}" method="post" target="_blank">
        <input type="hidden" name="phone_number" value="{phone_number}">
    </form>
    <script>
        document.getElementById("redirectForm").submit();
        // Redirect current tab back to /transactions
        window.location.href = "{url_for('transactions')}";
    </script>
    """
    return render_template_string(html)
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
