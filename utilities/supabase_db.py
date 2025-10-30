from supabase_lib.supabase_config import supabase
from supabase_lib.supabase_auth import *
from flask import redirect, url_for


# Create a new customer
def check_user_login():
    user = supabase.auth.get_session()
    # apputils.snack("red",f"user session {user}")
    return user
def session_timeout():
    print("Session Time Out..")
    apputils.snack("red",f"Session time out, Please Re-Login.")
    return redirect(url_for("login"))
def create_customer(name, dob, gender, phone_number, email, education, joining_for, address, profile_image):
    data = {
        "name": name,
        "dob": dob,
        "gender":gender,
        "phone_number": phone_number,
        "email": email,
        "education":education,
        "joining_for": joining_for,
        "address": address,
        "profile_image": profile_image,
    }
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout()
            apputils.snack("red","No active session. please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.table("Customers").insert(data).execute()
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")
    
    # supabase.auth.sign_out()

# Get all customers
def get_all_customers():
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout()
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.table("Customers").select("*").execute()
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")
    
# Get customer details
def get_customers_details(column_name,contact_number):
    isinternet=apputils.is_internet_available()
    try:
        user = check_user_login()

        if not user:
            session_timeout()
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.table("Customers").select("*").eq(column_name, contact_number).execute()
            # supabase.auth.sign_out()
            print(response.data)
            return response.data
    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")
# Update a customer
def update_customer(contact_number, updates):
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout()
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.table("Customers").update(updates).eq("phone_number", contact_number).execute()
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")

# Delete a customer
def delete_customer(customer_name):
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout() 
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.table("Customers").delete().eq("id", customer_name).execute()
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")

def get_all_customers_contact():
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout() 
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.rpc("get_phone_numbers").execute()
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")

def get_all_customers_names():
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout() 
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.rpc("get_names").execute()
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")
#  Add Transaction
def create_transaction(txn_date,transaction_type,amount,txn_made_by, payment_method, description, transaction_for,transaction_made_to):
    data = {
        "txn_date": txn_date,
        "txn_made_by": txn_made_by,
        "customer_transaction_type": transaction_type,
        "customer_amount": amount,
        "customer_payment_method": payment_method,
        "customer_description": description,
        "customer_transaction_for": transaction_for,
        "customer_transaction_made_to":transaction_made_to
    }
    # apputils.snack(color="green",msg=data)
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout() 
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            # response = supabase.rpc("insert_general_transactions", data).execute()
            response = supabase.rpc("insert_general_transactions", data).execute()
            # supabase.auth.sign_out()
            # apputils.snack(color="green",msg="Transaction Submitted Successfully!")
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")
    

#  Get All Transactions
def get_all_transactions():
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout() 
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.table("Transactions").select("*").execute()
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")
    
def get_transactionspagedata():
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
             
            session_timeout()
            # apputils.snack("red","No active session. Please Re-login.")
            print("SESSION TIME OUT.")
        elif not isinternet:
            print("No Internet Connection.")
            # apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.rpc("fetch_transaction_details").execute()
            #  
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")

def get_investmenttransactionspagedata():
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout() 
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.rpc("fetch_investment_transaction_details").execute()
            #  
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")
    
def get_subcriptionpagedata():
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout() 
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.rpc("fetch_subcription_details").execute()
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")
    
    
def get_net_profit(start_date,end_date):
    isinternet = apputils.is_internet_available()
    try:
        user = check_user_login()

        if not user:
            session_timeout()
        
        else:
            response = supabase.rpc("get_net_profit", {"start_date": start_date, "end_date": end_date}).execute()
            return response.data

    except Exception as e:
       return {"error": f"Error fetching data: {e}"}

def get_monthly_cash_upi(start_date,end_date):
    isinternet = apputils.is_internet_available()
    try:
        user = check_user_login()

        if not user:
            session_timeout()
        
        else:
            response = supabase.rpc("get_monthly_cash_upi", {"start_date": start_date, "end_date": end_date}).execute()
            return response.data

    except Exception as e:
       return {"error": f"Error fetching data: {e}"}

    
def get_investment_details(name):
    print("This is name -->",name)
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout() 
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.rpc("get_investment_details", {"staffname": str(name)}).execute()
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")
        
def get_expense_profit():
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout() 
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response_in = supabase.rpc("calculate_total_amount", {"filter_value": "IN"}).execute()
            response_out = supabase.rpc("calculate_total_amount", {"filter_value": "OUT"}).execute()
            # supabase.auth.sign_out()
            return response_in.data,response_out.data
            
    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")
    
#  Delete transaction by id 
def delete_transaction(transaction_id):
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout() 
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.table("Transactions").delete().eq("id", transaction_id).execute()
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")
    

def insert_addmission(data):
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout() 
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.rpc("insert_addmissions", data).execute()
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")

def insert_receipt_data(data):
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout() 
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.rpc("insert_receipt_data", data).execute()
            return response.data

    except Exception as e:
       apputils.snack("green",f"Error fetching user: {e}, Re-Login")

    

def run_sql(query):

    try:
        user = check_user_login()

        if not user:
            session_timeout()
        else:
            response = supabase.rpc("execute_sql", {"query": query}).execute()
            return response.data

    except Exception as e:
       apputils.snack("red",f"Issue --> {e}")
       print(f"Issue --> {e}")
       return {"error": f"Error fetching data: {e}"}
def upload_image(imagepath,imagename):
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout()    
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            with open(imagepath, "rb") as f:
                response = (
                    supabase.storage
                    .from_("customer_images")
                    .upload(
                        file=f,
                        path=f"{imagename}.png",
                        file_options={"content-type":"image/png"}
                    )
                )
            return response

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")
    
def get_profile_img(imagename):
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout()    
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = (
            supabase.storage
            .from_("customer_images")
            .get_public_url(f"{imagename}.png")
            )
            return response

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")

def search_profile_img(imagename):
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout()    
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = (
                supabase.storage
                .from_("customer_images")
                .list(
                    options = {
                        "limit": 100,
                        "offset": 0,
                        "sortBy": {"column": "name", "order": "desc"},
                        "search": imagename,
                    }
                )
            )
            if response:
                return get_profile_img(imagename)
            else:
                return "assets/img/blank_profile.png"
    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")

# Update a Receipt sent
def update_receipt_sent(receiptid):
    # {"is_sent": 1}
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout()
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.table("receipts").update({"is_sent": 1}).eq("receiptid", receiptid).execute()
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")

# Past 3 month collection and expense data 
def get_chart_data():
    # {"is_sent": 1}
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout()
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.rpc("get_last_three_months_summary").execute()
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")

def get_admission_chart_data():
    # {"is_sent": 1}
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout()
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.rpc("get_admissions_summary").execute()
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")


# Supabase QA functions---------
def insert_receipt_dataqa(data):
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout() 
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.rpc("insert_receipt_dataqa", data).execute()
            return response.data

    except Exception as e:
       apputils.snack("green",f"Error fetching user: {e}, Re-Login")

def insert_addmissionqa(data):
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout() 
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            response = supabase.rpc("insert_addmissionsqa", data).execute()
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")

def create_transactionqa(txn_date,transaction_type,amount,txn_made_by, payment_method, description, transaction_for,transaction_made_to):
    data = {
        "txn_date": txn_date,
        "txn_made_by": txn_made_by,
        "customer_transaction_type": transaction_type,
        "customer_amount": amount,
        "customer_payment_method": payment_method,
        "customer_description": description,
        "customer_transaction_for": transaction_for,
        "customer_transaction_made_to":transaction_made_to
    }
    apputils.snack(color="green",msg=data)
    isinternet = apputils.is_internet_available()

    try:
        user = check_user_login()

        if not user:
            session_timeout() 
            apputils.snack("red","No active session. Please Re-login.")
        elif not isinternet:
            apputils.snack("red", "No Internet Connection.")
        else:
            # response = supabase.rpc("insert_general_transactions", data).execute()
            response = supabase.rpc("qainsert_general_transactions", data).execute()
            # supabase.auth.sign_out()
            # apputils.snack(color="green",msg="Transaction Submitted Successfully!")
            return response.data

    except Exception as e:
       apputils.snack("red",f"Error fetching user: {e}, Re-Login")