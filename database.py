import mariadb
import random
import string
from datetime import datetime
from tkinter import messagebox

user_id = ""
passwrd = ""
id = 0

# Establish the database connection
class Start:
    def __init__(self):
        self.connection = mariadb.connect(
            host='192.168.128.35',
            user='jd',
            password='kali',
            database='food_waste'
        )
        self.cursor = self.connection.cursor()

s = Start()

def pswd(table_name, length=12):
    while True:
        now = datetime.now()
        date_part = now.strftime("%Y%m%d")  # Current date in YYYYMMDD format
        time_part = now.strftime("%H%M%S")  # Current time in HHMMSS format

        # Combine characters for the password
        characters = string.ascii_letters + string.digits + date_part + time_part

        # Generate a random password
        passwrd = ''.join(random.choice(characters) for _ in range(length))

        # Check for uniqueness in the database
        query = f"SELECT COUNT(*) FROM {table_name} WHERE PASSWORD = ?;"
        s.cursor.execute(query, (passwrd,))  # Pass as a tuple

        count = s.cursor.fetchone()[0]

        # If the password is unique, return it
        if count == 0:
            return passwrd


def user(table_name, name):
    while True:
        user_id = f"{name.lower().replace(' ', '_')}_{random.randint(1000, 9999)}"
        query = f"SELECT COUNT(*) FROM {table_name} WHERE USER_ID = ?;"

        try:
            s.cursor.execute(query, (user_id,))
        except mariadb.ProgrammingError as e:
            print(f"SQL Error: {e}")
            return None

        count = s.cursor.fetchone()[0]

        if count == 0:
            return user_id


def idd(table_name):
    query = f"SELECT MAX(ID) FROM {table_name}"
    s.cursor.execute(query)
    result = s.cursor.fetchone()
    return (result[0] + 1) if result[0] is not None else 1


def signup(name, table_name, email, ph, address, district, state, zip):
    global user_id, passwrd, id
    user_id = user(table_name, name)
    passwrd = pswd(table_name)
    id = idd(table_name)

    # Insert into DONOR table
    query = f"INSERT INTO {table_name} (ID, NAME, USER_ID, PASSWORD, EMAIL, PHONE_NO, ADDRESS, DISTRICT, STATE, ZIP) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
    s.cursor.execute(query, (id, name, user_id, passwrd, email, ph, address, district, state, zip))
    s.connection.commit()


def login(user_id, passwrd):
    query = "SELECT COUNT(*) FROM NGO WHERE USER_ID = ? AND PASSWORD = ?;"
    s.cursor.execute(query, (user_id, passwrd))
    count = s.cursor.fetchone()[0]

    if count == 1:
        return (1, "NGO")
    else:
        query = "SELECT COUNT(*) FROM DONOR WHERE USER_ID = ? AND PASSWORD = ?;"
        s.cursor.execute(query, (user_id, passwrd))
        count = s.cursor.fetchone()[0]

        if count == 1:
            return (1, "DONOR")
        else:
            return 0


def donate(user_id, food, quantity, exp_date):
    try:
        query = "SELECT NAME FROM DONOR WHERE USER_ID = ?"
        s.cursor.execute(query, (user_id,))
        name = s.cursor.fetchone()
        donor_name = name[0]

        query = "INSERT INTO donation (DONOR, FOOD, QUANTITY, EXPIRY_DATE) VALUES (?, ?, ?, ?)"
        s.cursor.execute(query, (donor_name, food, quantity, exp_date))
        s.connection.commit()
    except mariadb.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

def historyy(user_id) :
    query = "SELECT NAME FROM DONOR WHERE USER_ID = ?"
    s.cursor.execute(query, (user_id,))
    name = s.cursor.fetchone()
    donor_name = name[0]

    query = "Select FOOD,QUANTITY,EXPIRY_DATE from donation where DONOR = ?"
    s.cursor.execute(query,(donor_name,))
    donations = s.cursor.fetchall()

    items = []

    for donation in donations:
        item, quantity, date = donation
        items.append((item,quantity,date))

    s.connection.commit()

    return items

def status(user_id):
    query = "SELECT NAME FROM DONOR WHERE USER_ID = ?"
    s.cursor.execute(query, (user_id,))
    name = s.cursor.fetchone()
    donor_name = name[0]

    query = "Select Donation_ID,FOOD,QUANTITY,EXPIRY_DATE,STATUS from donation where DONOR = ? and STATUS <> 'Completed'"
    s.cursor.execute(query,(donor_name,))
    stat_query = s.cursor.fetchall()

    items = []

    for donation in stat_query:
        donation_id,food, quantity, exp_date ,stat= donation
        items.append((donation_id,food, quantity, exp_date,stat))

    s.connection.commit()

    return items

def update_status(donation_id,status) :

    query = "UPDATE donation SET status = ? WHERE donation_id = ?"
    s.cursor.execute(query,(status,donation_id))
    s.connection.commit()

def calculate_points(user_id):
    try:
        # Get the donor's name
        query = "SELECT NAME FROM DONOR WHERE USER_ID = ?"
        s.cursor.execute(query, (user_id,))
        name = s.cursor.fetchone()

        if name is None:
            return 0  # If donor is not found, return 0 points

        donor_name = name[0]

        # Get the number of completed donations
        query = "SELECT COUNT(*) FROM donation WHERE DONOR = ? AND STATUS = 'Completed';"
        s.cursor.execute(query, (donor_name,))
        completed_donations = s.cursor.fetchone()[0]

        # Calculate points (e.g., 10 points per completed donation)
        points = completed_donations * 10

        return points
    except mariadb.Error as e:
        print(f"Database Error: {e}")
        return 0  # Return 0 points in case of error
def stop():
    s.cursor.close()
    s.connection.close()


# print(status("JD_1"))
