from twilio.rest import Client
import random
import api 

from mail import send_email

account_sid = api.YOUR_ACCOUNT_SID
auth_token = api.YOUR_AUTH_TOKEN

client = Client(account_sid, auth_token)

def generate_otp():
    return random.randint(1000, 9999)
number = '+91'
def send_otp(phone_number):
    global number
    otp = generate_otp()
    number = number +phone_number
    message = client.messages.create(
        body=f"Your OTP is {otp}",
        from_='+18507833937',  
        to=number                
    )
    print(f"OTP sent: {otp}")
    return otp
