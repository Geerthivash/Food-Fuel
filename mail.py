import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random

def send_email(to):
    # Create a multipart email
    msg = MIMEMultipart()
    msg['From'] = 'Food Fuel <geerthi006@gmail.com>'
    msg['To'] = to
    msg['Subject'] = "Sign up OTP"

    otp = random.randint(1000, 9999)

    body = (
        f"\nHi\n\n"
        f"As you are trying to register, here is the OTP that you need to\n"
        f"enter to confirm your email address. If you didn't make this\n"
        f"request, please ignore this email.\n\n"
        f"\t\t\t\t\tOTP : {otp}\n\n"
        f"If you still face any difficulties or have any other support-related queries, feel free to write to us at\n"
        f"geerthi006@duck.com"
    )
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Upgrade the connection to TLS
            # Login to the SMTP server
            server.login('geerthi006@gmail.com', 'giie zobt cgno obhp')
            text = msg.as_string()  # Convert the message to a string
            server.sendmail(msg['From'], to, text)  # Send the email
        return otp  # Return the OTP for further use
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
