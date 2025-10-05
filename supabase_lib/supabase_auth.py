from utilities import apputils
from supabase import create_client, Client
from gotrue.errors import AuthApiError

# Replace these with your Supabase Project details
SUPABASE_URL = "https://dvobjzoqovdrsuzhjnkf.supabase.co"  # From the Supabase Dashboard
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR2b2Jqem9xb3ZkcnN1emhqbmtmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzIzNzY5MjUsImV4cCI6MjA0Nzk1MjkyNX0.YiMofxYQxrp4YjO3zdSB2pThHXY62KJRppmZLxaFGBo"  # From the API Settings

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def login_with_email_password(email, password):
    response= None
    try:
        # Sign in using the 'auth' method
        isinternet=apputils.is_internet_available()
        if isinternet:
            response =  supabase.auth.sign_in_with_password({"email": email, "password": password})
            return response  # Return user details on success
        else:
            apputils.snack("red","No Internet Connection..")
    except AuthApiError as e:  #gotrue.errors.AuthRetryableError: [Errno 8] nodename nor servname provided, or not known
        dialog = dialog_element(title="Login Failed",text=f"Error! {e}")
        dialog.open()
        return None
    # except Exception as e:
    #     error_message = str(e)
    #     if "EMAIL_NOT_FOUND" in error_message:
    #         dialog = dialog_element(title="Login Failed",text="User not found. Please check your email.")
            
    #     elif "INVALID_PASSWORD" in error_message:
    #         dialog = dialog_element(title="Login Failed",text="Incorrect password. Please try again.")
            
    #     else:
    #         dialog = dialog_element(title="Login Failed",text="Failed to login. Please check your credentials.")
            
    #     dialog.open()
    #     return None
def logout():
    isinternet=apputils.is_internet_available()
    if isinternet:
        supabase.auth.sign_out()
    else:
        apputils.snack("red","No Internet Connection..")
def dialog_element(title,text):
    print(f"{title} --> {text}")
    # return element
def send_password_reset_email(email):
    pass
    # try:
    #     pauth.send_password_reset_email(email)
    #     return True
    # except Exception as e:
    #     print(f"Error sending reset email: {e}")
    #     return False