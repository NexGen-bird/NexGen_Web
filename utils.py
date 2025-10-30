from urllib.parse import quote
import json
from datetime import datetime, date

def create_whatsapp_url(phone_number, message=""):
    """Create a WhatsApp URL for direct messaging"""
    # Remove any non-numeric characters and ensure it starts with country code
    phone = ''.join(filter(str.isdigit, phone_number))
    if not phone.startswith('91'):  # Assuming India country code
        phone = '91' + phone
    
    encoded_message = quote(message)
    return f"https://wa.me/{phone}?text={encoded_message}"

def get_whatsapp_receipt_message(customer_name, amount, plan, start_date, end_date):
    """Generate a predefined WhatsApp message for receipts"""
    message = f"""Dear {customer_name},

Thank you for your payment at NEXGEN Study Centre! 🎓

📄 Receipt Details:
💰 Amount: ₹{amount}
📅 Plan: {plan}
🗓️ Start Date: {start_date.strftime('%d/%m/%Y')}
🗓️ End Date: {end_date.strftime('%d/%m/%Y')}

We're excited to support your learning journey! 📚✨

Best regards,
NEXGEN Study Centre Team"""
    return message
def get_receipt_link_msg(customer_name,receiptID):
    url = f"https://nexgeninvoicetracker.onrender.com/receipt/{str(receiptID)}"
    final_message = f"""
Hi {customer_name},
Please find your receipt at the link below,

Steps to download your receipt:
1. Click on the link
2. Enter your registered mobile number
3. View and download your receipt

{url}

If you face any issues, feel free to reply to this message.
Thank you for choosing NexGen Self Study Center!
"""
    return final_message
def get_whatsapp_expiry_reminder(customer_name, expiry_date):
    """Generate a predefined WhatsApp message for expiry reminders"""
    message = f"""Dear {customer_name},

Subscription Expiry Reminder

This is a reminder that your NexGen Study Center subscription is expiring on *{expiry_date}*.

 To avoid any interruption in your study schedule, please renew your subscription at the earliest.

You can reply to this message or contact us directly for assistance.

Thank you for choosing NexGen Study Center! 

Best regards,
NEXGEN Study Centre Team"""
    return message

def calculate_age(birth_date):
    """Calculate age from birth date"""
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def format_currency(amount):
    """Format amount as Indian currency"""
    print(f"₹{amount}")

def format_currency_denomination(amount):
    """Format amount in K, L, Cr denominations"""
    if amount >= 10000000:  # 1 Crore
        return f"₹{amount/10000000:.1f}Cr"
    elif amount >= 100000:  # 1 Lakh
        return f"₹{amount/100000:.1f}L"
    elif amount >= 1000:    # 1 Thousand
        return f"₹{amount/1000:.1f}K"
    else:
        return f"₹{amount:,.0f}"

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")
