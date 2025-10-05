import os
import configparser
import socket
import json
from flask import flash
selected_group = ""
def is_internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

def snack(color,msg):
    cate = "danger" if color == "red" else "success"
    return flash(msg,cate)
def baseurl():
    config = configparser.ConfigParser()
    config.read('project_config.conf')

    url = config["Base_URL"]["base_url"]
    return url
from datetime import datetime

def get_background_color(planexpirydate):
    today = datetime.today().date()
    expiry_date = datetime.strptime(planexpirydate, "%Y-%m-%d").date()
    days_left = (expiry_date - today).days
    print("Days Left--> ",days_left)
    if days_left <= 0:
        return "#cc3300"  # Red (Expiring today)
    elif days_left == 1:
        return "#ff4d4d"  # Light Red
    elif days_left == 2:
        return "#ff9966"  # Orange
    elif days_left == 3:
        return "#FFBF69"  # Light Orange
    elif 4 <= days_left <= 7:
        return "#ffcc00"  # Yellow
    else:
        return "#339900"  # Light Green (More than a week left)

def date_format(input_date):

    # Input date string
    # input_date = '2024-11-28T16:30:12.257328+00:00'

    # Convert to datetime object
    if not input_date:
        return ""
    try:
        date_obj = datetime.fromisoformat(input_date)

        # Format the date to desired format
        formatted_date = date_obj.strftime('%d %b %Y')

        return formatted_date
    except Exception:
        return input_date

from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta

def calculate_end_dates1(input_date,plantype):
    """
    This function calculates the end dates for a given input date based on 
    Month, Quarter, Half Year, and Year durations.

    Parameters:
        input_date (str): Date in the format 'YYYY-MM-DD'

    Returns:
        dict: A dictionary containing the end dates for Month, Quarter, Half Year, and Year
    """
    # Parse the input date string to a datetime object
    start_date = datetime.strptime(str(input_date), '%Y-%m-%d').date()

    # Calculate the end dates
    if plantype =="Monthly": 
        end_date = start_date + relativedelta(months=1) - relativedelta(days=1)  # Add 1 month
    elif plantype=="Quaterly":
        end_date = start_date + relativedelta(months=3) - relativedelta(days=1) # Add 3 months
    elif plantype=="Half Yearly": 
        end_date =start_date + relativedelta(months=6) - relativedelta(days=1),  # Add 6 months
    elif plantype=="Yearly": 
        end_date =start_date + relativedelta(years=1)   # Add 1 year
    
    print("End Date --> ",str(end_date))
    return str(start_date),str(end_date)

def calculate_end_dates(input_date, plantype):
    """
    Calculates the end date based on the input date and plan type,
    reducing one day from the final calculated end date.

    Parameters:
        input_date (str): Date in the format 'YYYY-MM-DD'
        plantype (str): Type of plan duration ('Month', 'Quarter', 'Half Year', 'Year')

    Returns:
        tuple: A tuple containing start date and end date as datetime.date objects
    """
    try:
        # Parse the input date string to a date object
        start_date = datetime.strptime(str(input_date), '%Y-%m-%d').date()
    except ValueError:
        print("red","Invalid input date format. Use 'YYYY-MM-DD'.")
        # raise ValueError("Invalid input date format. Use 'YYYY-MM-DD'.")

    # Map plan types to duration
    durations = {
        2: relativedelta(months=1),
        3: relativedelta(months=3),
        4: relativedelta(months=6),
        5: relativedelta(years=1),
        6: relativedelta(months=1),
        1: relativedelta(days=1)
        
    }

    if plantype not in durations:
        print("red","Choose from 'Month', 'Quarter', 'Half Year', or 'Year'.")
        # raise ValueError("Invalid plan type. Choose from 'Month', 'Quarter', 'Half Year', or 'Year'.")

    # Calculate the end date and reduce one day
    end_date = start_date + durations[plantype] - relativedelta(days=1)  # Subtract 2 days

    return str(start_date), str(end_date)
def get_plan_from_id(id=2):
   data_dic = {2: 'Monthly',
    3: 'Quarterly', 
    4: 'Half Yearly', 
    5: 'Yearly', 
    1: 'Day', 
    6:'Weekend'}
   return data_dic[int(id)] if int(id) in data_dic else "NA"
def get_current_period_range(input_date=None):
    """
    Returns the correct period based on the input date.
    - If the date is before the 15th, returns the previous period (15th of last month → 14th of this month).
    - If the date is 15th or later, returns the current period (15th of this month → 14th of next month).
    
    If input_date is not provided, it defaults to today's date.
    """
    if input_date is None:
        input_date = date.today()

    if input_date.day < 15:
        # Before the 15th, return the previous period
        if input_date.month == 1:
            start_date = date(input_date.year - 1, 12, 15)  # Previous year December
            end_date = date(input_date.year, 1, 14)  # Current January 14
        else:
            start_date = date(input_date.year, input_date.month - 1, 15)  # Previous month 15th
            end_date = date(input_date.year, input_date.month, 14)  # Current month 14th
    else:
        # On or after the 15th, return the current period
        start_date = date(input_date.year, input_date.month, 15)

        if input_date.month == 12:
            end_date = date(input_date.year + 1, 1, 14)  # Next year January 14
        else:
            end_date = date(input_date.year, input_date.month + 1, 14)  # Next month 14th

    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
def write_json_file(filename, username, password,is_remember):
    """Writes a JSON file with the given username and password."""
    data = [{"username": username, "password": password,"is_remember":str(is_remember)}]
    
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def read_json_file(filename):
    """Reads and returns the data from the JSON file."""
    try:
        with open(filename, "r") as file:
            data = json.load(file)
        return data[0]
    except FileNotFoundError:
        print("File not found.")
        return None

from datetime import datetime

def add_current_time_to_date(date_str):
    """
    Takes a date string (YYYY-MM-DD) and adds the current time (HH:MM:SS.ffffff).
    
    :param date_str: str, Date in 'YYYY-MM-DD' format
    :return: str, Timestamp in 'YYYY-MM-DD HH:MM:SS.ffffff' format
    """
    # Convert the input date string to a datetime object
    date_part = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    # Get the current time
    current_time = datetime.now().time()
    
    # Combine the date with the current time
    full_datetime = datetime.combine(date_part, current_time)
    
    # Format the result
    return full_datetime.strftime("%Y-%m-%d %H:%M:%S")
def format_inr(amount):
    s = str(amount)
    if len(s) <= 3:
        return s
    else:
        return s[:-3][::-1].replace(
            s[:-3][::-1], 
            ",".join([s[:-3][::-1][i:i+2] for i in range(0, len(s[:-3]), 2)])
        )[::-1] + "," + s[-3:]
def format_number(n: float) -> str:
    """
    Convert a number into a readable format using absolute values, K (thousand), L (lakh), and Cr (crore).
    
    Args:
        n (float): The number to be formatted.
    
    Returns:
        str: The formatted number as a string.
    """
    abs_n = abs(n)
    
    if abs_n >= 10**7:  # Crore
        value = n / 10**7
        suffix = " Cr"
    elif abs_n >= 10**5:  # Lakh
        value = n / 10**5
        suffix = " L"
    elif abs_n >= 10**3:  # Thousand
        value = n / 10**3
        suffix = " K"
    else:
        value = n
        suffix = ""
    
    # Format the number, removing .00 if whole
    formatted = f"{value:.2f}".rstrip("0").rstrip(".") + suffix
    
    return formatted

def get_shift_text(shift_list):
    shift_list = list(map(int, shift_list))
    shift_times = {
        1: "6am to 12pm",
        2: "12pm to 6pm",
        3: "6pm to 12am",
        4: "12am to 6am"
    }
    
    def get_ordinal(n):
        if 10 <= n % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix}"
    
    if not shift_list:
        return "No shifts selected"
    
    shift_list = sorted(set(shift_list))  # Remove duplicates and sort
    
    # Check for single shift
    if len(shift_list) == 1:
        shift = shift_list[0]
        return f"{get_ordinal(shift)} shift ({shift_times[shift]})"
    
    # Check for consecutive shifts
    if all(shift_list[i] + 1 == shift_list[i + 1] for i in range(len(shift_list) - 1)):
        start_time = shift_times[shift_list[0]].split(" to ")[0]
        end_time = shift_times[shift_list[-1]].split(" to ")[1]
        return f"{len(shift_list)} shifts ({start_time} to {end_time})"
    
    # Non-continuous shifts
    shift_positions = [get_ordinal(shift) for shift in shift_list]
    return " & ".join(shift_positions) + " shifts"