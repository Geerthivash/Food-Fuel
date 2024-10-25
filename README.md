# Food-Fuel :
FoodFuel, a platform connecting food donors with NGOs to reduce food wastage and enhance access to food for those in need

## database.py:

```py
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

```

## donor_dash.py:

```py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
from database import donate,historyy,status,update_status,calculate_points
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

fade_direction = 1  # 1 for fading in, -1 for fading out
fade_speed = 0.05  # How much to change opacity by each step (adjust for speed)
current_alpha = 0.0

current_image_index = 0


def image(root):
    logo_path = "D:\\logo2.png"
    logo_b = Image.open(logo_path)
    logo_b = logo_b.resize((220, 70), Image.Resampling.LANCZOS)  # Resize the image if needed
    logo_b_tk = ImageTk.PhotoImage(logo_b)
    logo_label = tk.Label(root, image=logo_b_tk, borderwidth=0)
    logo_label.place(x=89, y=90)

def d_main(user_id,org_type):
    root = ctk.CTk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 1480
    window_height = 840
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    ctk.set_appearance_mode("dark")  # Can switch to "dark"
    root.configure(fg_color="#ffffff")

    card_frame = ctk.CTkFrame(root)

    dummy_frame = ctk.CTkFrame(root, fg_color="lightblue", corner_radius=10)

    plot_frame = tk.Frame(root)

    # def donation():
    #     app = ctk.CTk()
    #     screen_width = app.winfo_screenwidth()
    #     screen_height = app.winfo_screenheight()
    #     window_width = 700
    #     window_height = 400
    #     x = (screen_width // 2) - (window_width // 2)
    #     y = (screen_height // 2) - (window_height // 2)
    #     app.geometry(f"{window_width}x{window_height}+{x}+{y}")
    #     ctk.set_appearance_mode("light")  # Can switch to "dark"
    #     app.configure(fg_color="#ffffff")
    #
    #     def submit_donation():
    #         # Get the values from the input fields
    #         food = food_entry.get()
    #         quantity = quantity_entry.get()
    #         expiry_date = expiry_date_entry.get()
    #
    #         if not food or not quantity or not expiry_date:
    #             messagebox.showerror("Input Error", "All fields are required")
    #             return
    #
    #         try:
    #             quantity = float(quantity)  # Ensure quantity is numeric
    #         except ValueError:
    #             messagebox.showerror("Input Error", "Quantity must be a number")
    #             return
    #
    #         donate(user_id,food,quantity,expiry_date)
    #
    #         # Show success message
    #         messagebox.showinfo("Success", f"Donation of {food} added successfully!")
    #         # Clear the fields after submission
    #         food_entry.delete(0, 'end')
    #         quantity_entry.delete(0, 'end')
    #         expiry_date_entry.delete(0, 'end')
    #         app.destroy()
    #
    #     # Food Label and Entry
    #     food_label = ctk.CTkLabel(app, text="Food")
    #     food_label.pack(pady=10)
    #     food_entry = ctk.CTkEntry(app, width=200)
    #     food_entry.pack()
    #
    #     # Quantity Label and Entry
    #     quantity_label = ctk.CTkLabel(app, text="Quantity (in kg or units)")
    #     quantity_label.pack(pady=10)
    #     quantity_entry = ctk.CTkEntry(app, width=200)
    #     quantity_entry.pack()
    #
    #     # Expiry Date Label and Entry
    #     expiry_date_label = ctk.CTkLabel(app, text="Expiry Date (YYYY-MM-DD)")
    #     expiry_date_label.pack(pady=10)
    #     expiry_date_entry = ctk.CTkEntry(app, width=200)
    #     expiry_date_entry.pack()
    #
    #     # Submit Button
    #     submit_button = ctk.CTkButton(app, text="Submit", command=submit_donation)
    #     submit_button.pack(pady=20)
    #
    #     app.mainloop()

    def donation():
        app = ctk.CTk()
        screen_width = app.winfo_screenwidth()
        screen_height = app.winfo_screenheight()
        window_width = 700
        window_height = 400
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        app.geometry(f"{window_width}x{window_height}+{x}+{y}")
        ctk.set_appearance_mode("light")  # Can switch to "dark"
        app.configure(fg_color="#ffffff")

        def submit_items_count():
            try:
                items_count = int(items_count_entry.get())  # Ensure the input is numeric
            except ValueError:
                messagebox.showerror("Input Error", "Number of food items must be a number")
                return

            if items_count <= 0:
                messagebox.showerror("Input Error", "Please enter a valid number of food items")
                return

            # Hide the current widgets and show the dynamic form for food items
            items_count_label.pack_forget()
            items_count_entry.pack_forget()
            submit_items_button.pack_forget()

            create_food_form(items_count)

        def create_food_form(items_count):
            food_entries = []
            quantity_entries = []
            expiry_date_entries = []

            def submit_donation():
                for i in range(items_count):
                    food = food_entry.get()
                    quantity = quantity_entry.get()
                    expiry_date = expiry_date_entry.get()

                    if not food or not quantity or not expiry_date:
                        messagebox.showerror("Input Error", f"All fields are required for item {i + 1}")
                        return

                    try:
                        quantity = float(quantity)  # Ensure quantity is numeric
                    except ValueError:
                        messagebox.showerror("Input Error", f"Quantity for item {i + 1} must be a number")
                        return

                    # Collect each food donation data
                    food_entries.append(food)
                    quantity_entries.append(quantity)
                    expiry_date_entries.append(expiry_date)
                # Process each food donation
                for j in range(items_count):
                    donate(user_id, food_entries[j], quantity_entries[j], expiry_date_entries[j])  # Assuming donate is your functio


                # Show success message
                messagebox.showinfo("Success", "Donation added successfully!")
                app.destroy()  # Close the form window

            # Create input fields dynamically based on the number of items
            for i in range(items_count):
                food_label = ctk.CTkLabel(app, text=f"Food {i + 1}")
                food_label.pack(pady=5)
                food_entry = ctk.CTkEntry(app, width=200)
                food_entry.pack()
                # food_entries.append(food_entry)

                quantity_label = ctk.CTkLabel(app, text=f"Quantity (in kg or units) {i + 1}")
                quantity_label.pack(pady=5)
                quantity_entry = ctk.CTkEntry(app, width=200)
                quantity_entry.pack()
                # quantity_entries.append(quantity_entry)

                expiry_date_label = ctk.CTkLabel(app, text=f"Expiry Date (YYYY-MM-DD) {i + 1}")
                expiry_date_label.pack(pady=5)
                expiry_date_entry = ctk.CTkEntry(app, width=200)
                expiry_date_entry.pack()
                # expiry_date_entries.append(expiry_date_entry)

            # Submit button after adding all items
            submit_button = ctk.CTkButton(app, text="Submit Donation", command=submit_donation)
            submit_button.pack(pady=20)

        # Initial input to ask how many food items are being donated
        items_count_label = ctk.CTkLabel(app, text="How many food items are you donating?")
        items_count_label.pack(pady=10)
        items_count_entry = ctk.CTkEntry(app, width=100)
        items_count_entry.pack()

        # Button to submit the number of items
        submit_items_button = ctk.CTkButton(app, text="Submit", command=submit_items_count)
        submit_items_button.pack(pady=20)

        app.mainloop()

    def dashboard():
        dash_button.configure(fg_color="#FFB84D",bg_color="#FFFFFF",corner_radius=9)
        history_button.configure(bg_color="#FFFFFF", text_color="#606060", fg_color="#FFFFFF")
        impact_button.configure(bg_color="#FFFFFF", text_color="#606060", fg_color="#FFFFFF")
        # contact_button.configure(bg_color="#FFFFFF", text_color="#606060", fg_color="#FFFFFF")

        card_frame.place_forget()
        plot_frame.place_forget()
        update_points_label(user_id)
        def get_faded_color(intensity):
            value = int(255 * intensity)  # Scale intensity to RGB values (0-255)
            hex_value = f"{value:02x}"
            return f"#{hex_value}{hex_value}{hex_value}"

        def fade_text():
            global current_alpha, fade_direction

            # Adjust current transparency
            current_alpha += fade_speed * fade_direction

            # If fully visible or fully invisible, reverse direction
            if current_alpha >= 1.0:  # Fully visible
                fade_direction = -1  # Start fading out
            elif current_alpha <= 0.0:  # Fully invisible
                fade_direction = 1  # Start fading in

            # Change the button's text color by updating the hex value based on alpha
            faded_color = get_faded_color(current_alpha)
            donate_now_button.configure(text_color=faded_color)

            # Continue the fade effect
            root.after(80, fade_text)
        fade_text()

        b_label.place(x=450, y=200)
        p_label.place(x=50,y=670)
        donate_now_button.place(x=545, y=281)
        welcome_label.place(x=369, y=95)
        status_label.place(x=1195,y=160)
        points_label.place(x=144,y=583)
        def status_update(user_id):
            # Fetch the donations for the user
            donations = status(user_id)

            # Create a frame to display the donations

            dummy_frame.configure(border_width=2, border_color="gray")
            dummy_frame.place(x=1110, y=200)

            if donations != []:
                # Loop through each donation and create a row with the item and a dropdown for status
                for index, donation in enumerate(donations):
                    donation_id, item, quantity, date, stat = donation

                    # Display the donation item and quantity
                    item_label = ctk.CTkLabel(dummy_frame, text=f"{item} - {quantity} ({date})",text_color="black")
                    item_label.grid(row=donation_id, column=0, padx=10, pady=10)

                    # Create a dropdown (combobox) for the status with options
                    status_var = ctk.StringVar(value=stat)
                    status_dropdown = ctk.CTkOptionMenu(
                        dummy_frame,
                        variable=status_var,
                        values=["Pending", "Completed", "Scheduled", "Cancelled"],
                        command=lambda new_status, donation_id=donation_id: update_status(donation_id, new_status)
                    )
                    status_dropdown.grid(row=donation_id, column=1, padx=10, pady=10)


            else:
                dummy_frame.place_forget()
                frame1.place(x=1170,y=200)
                text_label.pack(pady=10)
        status_update(user_id)

        # def start_transition(image_label, image_files, transition_duration):
        #     global current_image_index  # Use a global variable to keep track of the current image index
        #
        #     # Open the current image
        #     image = Image.open(image_files[current_image_index])
        #
        #     # Resize the image to 300x300 using LANCZOS
        #     resized_image = image.resize((500, 360), resample=Image.LANCZOS)
        #
        #     # Convert to PhotoImage and update the label
        #     photo = ImageTk.PhotoImage(resized_image)
        #     image_label.configure(image=photo)
        #     image_label.image = photo  # Keep a reference to prevent garbage collection
        #
        #     # Update the current image index
        #     current_image_index = (current_image_index + 1) % len(image_files)
        #
        #     # Schedule the next image transition
        #     image_label.after(transition_duration, start_transition, image_label, image_files, transition_duration)
        #
        # start_transition(image_label, image_files, transition_duration=4000)

    def history():
        b_label.place_forget()
        donate_now_button.place_forget()
        welcome_label.place_forget()
        frame1.place_forget()
        text_label.place_forget()
        status_label.place_forget()
        dummy_frame.place_forget()
        plot_frame.place_forget()

        history_button.configure(fg_color="#FFB84D",bg_color="#FFFFFF",corner_radius=9)
        dash_button.configure(bg_color="#FFFFFF", text_color="#606060", fg_color="#FFFFFF")
        impact_button.configure(bg_color="#FFFFFF", text_color="#606060", fg_color="#FFFFFF")
        # contact_button.configure(bg_color="#FFFFFF", text_color="#606060", fg_color="#FFFFFF")

        donations = historyy(user_id)

        colors = ['cyan', 'lightgreen', 'lightcoral', 'orchid', 'gold', 'lightblue', 'lightyellow', 'lightpink', 'lightgray', 'lightcyan', 'lavender', 'lightsalmon', 'palegreen', 'khaki', 'lightseagreen', 'lightsteelblue', 'lightcoral', 'peachpuff', 'rosybrown', 'lightskyblue', 'powderblue', 'lightgoldenrodyellow', 'cyan', 'lavender', 'honeydew']


        # Create a frame to hold the cards and allow grid layout
        card_frame.place(x=390, y=170)
        card_frame.configure(fg_color="white")

        max_columns = 5  # Maximum cards per row
        k = 0
        for index, donation in enumerate(donations):
            row = index // max_columns  # Calculate the row (integer division)
            column = index % max_columns  # Calculate the column (remainder)


            color = colors[k]
            food, quantity, expiry = donation
            k += 1

            # Create a card with a specific background color
            card = ctk.CTkFrame(card_frame, fg_color=color, corner_radius=10)
            card.grid(row=row, column=column, padx=10, pady=10)  # Position cards in grid
            # card.grid_propagate(False)  # Prevent the card from resizing to fit its content


            # Card content: food, quantity, and expiry date
            food_label = ctk.CTkLabel(card, text=f"Food: {food}", text_color="black")
            food_label.pack(anchor='w', padx=10, pady=5)
            quantity_label = ctk.CTkLabel(card, text=f"Quantity: {quantity}", text_color="black")
            quantity_label.pack(anchor='w', padx=10)
            expiry_label = ctk.CTkLabel(card, text=f"Delivered Date: {expiry}", text_color="black")
            expiry_label.pack(anchor='w', padx=10, pady=5)

    def impact():
        impact_button.configure(fg_color="#FFB84D",bg_color="#FFFFFF",corner_radius=9)
        dash_button.configure(bg_color="#FFFFFF", text_color="#606060", fg_color="#FFFFFF")
        history_button.configure(bg_color="#FFFFFF", text_color="#606060", fg_color="#FFFFFF")
        # contact_button.configure(bg_color="#FFFFFF", text_color="#606060", fg_color="#FFFFFF")

        b_label.place_forget()
        donate_now_button.place_forget()
        welcome_label.place_forget()
        frame1.place_forget()
        text_label.place_forget()
        status_label.place_forget()
        dummy_frame.place_forget()

        def create_plot():
            # Example donation data over different events
            dates = ['2024-10-01', '2024-10-05', '2024-10-12']
            families_served = [2, 3, 10]  # Number of families served
            food_saved = [100, 184, 534]  # Total food saved from waste

            # Convert dates to a more suitable format for plotting
            x = np.arange(len(dates))  # x positions for each date

            # Create a Matplotlib figure with a new size
            fig = Figure(figsize=(14, 8))  # Change the size here (width, height)
            ax = fig.add_subplot(111)

            # Plotting each line with a different color and style
            ax.plot(x, families_served, marker='s', label='Number of Families Served', color='dodgerblue', linewidth=3,
                    markersize=8)
            ax.plot(x, food_saved, marker='D', label='Total Food Saved from Waste', color='orangered', linewidth=3,
                    markersize=8)

            # Customize the plot
            ax.set_xticks(x)
            ax.set_xticklabels(dates, fontsize=12, fontweight='bold')
            ax.set_ylabel('Count', fontsize=14, fontweight='bold')
            ax.set_title('Impact of Donations on Society Over Time', fontsize=18, fontweight='bold')
            ax.legend(fontsize=12, loc='upper left')
            ax.set_facecolor('#f0f0f0')  # Light grey background
            ax.grid(False)  # Removing grid lines

            # Adding annotations for emphasis
            for i in range(len(dates)):
                ax.annotate(f'{families_served[i]}', (x[i], families_served[i]), textcoords="offset points",
                            xytext=(0, 10), ha='center', fontsize=10, color='dodgerblue')
                ax.annotate(f'{food_saved[i]}', (x[i], food_saved[i]), textcoords="offset points", xytext=(0, 10),
                            ha='center', fontsize=10, color='orangered')

            return fig


        plot_frame.place(x=350, y=180)  # Change x, y to position the frame

        # Create the plot
        fig = create_plot()

        # Create a canvas to embed the Matplotlib figure
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


    # def contact():
    #     contact_button.configure(fg_color="#FFB84D",bg_color="#FFFFFF",corner_radius=9)
    #     dash_button.configure(bg_color="#FFFFFF", text_color="#606060", fg_color="#FFFFFF")
    #     history_button.configure(bg_color="#FFFFFF", text_color="#606060", fg_color="#FFFFFF")
    #     impact_button.configure(bg_color="#FFFFFF", text_color="#606060", fg_color="#FFFFFF")
    #
    #     b_label.place_forget()
    #     donate_now_button.place_forget()
    #     welcome_label.place_forget()
    #     frame1.place_forget()
    #     text_label.place_forget()
    #     status_label.place_forget()
    #     dummy_frame.place_forget()




    def create_circle_image(image_path, size):
        img = Image.open(image_path).resize((size, size), Image.Resampling.LANCZOS)

        # Create a circular mask
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)  # Draw a circle

        # Apply the mask to the image to make it circular
        img = img.convert("RGBA")
        img.putalpha(mask)

        # Create a new image with a white background to avoid transparency issues
        background = Image.new("RGBA", (size, size), "white")  # Transparent background
        final_img = Image.alpha_composite(background, img)

        return final_img

    def update_points_label(user_id):
        points = calculate_points(user_id)  # Get points from database
        points_label.configure(text=f"{points}")

    def logout():
        root.destroy()

    # banner in dashboard

    banner_path = "D:\\banner.png"
    img_b = Image.open(banner_path)
    img_b = img_b.resize((880, 220), Image.Resampling.LANCZOS)  # Resize the image if needed
    img_b_tk = ImageTk.PhotoImage(img_b)
    b_label = tk.Label(root, image=img_b_tk, borderwidth=0)

    point_path = "D:\\point.png"
    img_p = Image.open(point_path)
    img_p = img_p.resize((260, 150), Image.Resampling.LANCZOS)  # Resize the image if needed
    img_p_tk = ImageTk.PhotoImage(img_p)
    p_label = tk.Label(root, image=img_p_tk, borderwidth=0)

    #icons in dashboard

    dashboard_icon = Image.open("D:\\dash.png")
    r_dashboard_icon = dashboard_icon.resize((30,30))
    dashboard_icon = ImageTk.PhotoImage(r_dashboard_icon)

    history_icon = Image.open("D:\\history.png")
    r_history_icon = history_icon.resize((30, 30))
    history_icon = ImageTk.PhotoImage(r_history_icon)

    impact_icon = Image.open("D:\\impact.png")
    r_impact_icon = impact_icon.resize((30, 30))
    impact_icon = ImageTk.PhotoImage(r_impact_icon)


    log_out_icon = Image.open("D:\\log_out_icon.png")
    r_log_out_icon = log_out_icon.resize((20, 20))
    log_out_icon = ImageTk.PhotoImage(r_log_out_icon)

    #buttons in dashboard

    dash_button = ctk.CTkButton(root, text="DASHBOARD",font=("ROBOTO", 15.5),corner_radius=9, width=178,bg_color="#FFFFFF",text_color="#606060" ,fg_color="#FFFFFF",hover_color="#FFB84D",command = dashboard,image=dashboard_icon, compound="left")
    dash_button.place(x=50, y=200)

    history_button = ctk.CTkButton(root, text="HISTORY", font=("ROBOTO", 15.5), corner_radius=9, width=155,bg_color="#FFFFFF", text_color="#606060", fg_color="#FFFFFF", hover_color="#FFB84D",command=history,image=history_icon, compound="left")
    history_button.place(x=53, y=260)

    impact_button = ctk.CTkButton(root, text="IMPACT", font=("ROBOTO", 15.5), corner_radius=9, width=155,bg_color="#FFFFFF", text_color="#606060", fg_color="#FFFFFF", hover_color="#FFB84D",command=impact,image=impact_icon, compound="left")
    impact_button.place(x=52, y=320)

    # contact_button = ctk.CTkButton(root, text="CONTACT", font=("ROBOTO", 15.5), corner_radius=9, width=155,bg_color="#FFFFFF", text_color="#606060", fg_color="#FFFFFF", hover_color="#FFB84D",command=contact,image=contact_icon, compound="left")
    # contact_button.place(x=52, y=380)

    # soft_name_label = ctk.CTkLabel(root , text="FoodFuel", font=("Bahnschrift SemiCondensed",26,"bold"), text_color="black", bg_color="white")
    # soft_name_label.place(x=69,y=60)
    logo_path = "D:\\logos.png"
    logo_b = Image.open(logo_path)
    logo_b = logo_b.resize((220, 70), Image.Resampling.LANCZOS)  # Resize the image if needed
    logo_b_tk = ImageTk.PhotoImage(logo_b)
    logo_label = tk.Label(root, image=logo_b_tk, borderwidth=0)
    logo_label.place(x=69, y=90)

    donate_now_button = ctk.CTkButton(root, text="Donate Now", font=("Tahoma", 16.5, "bold"), corner_radius=0, width=0,bg_color="#000032", text_color="#ffffff", fg_color="#000032",hover_color="#000032",command=donation)

    logout_button = ctk.CTkButton(root, text="Log Out", font=("Helvetica", 16.5), corner_radius=0, width=0,bg_color="#ffffff", text_color="red", fg_color="#ffffff",hover_color="#ffffff",command=logout, image=log_out_icon, compound="right")
    logout_button.place(x=83, y=771)



    #labels in dashboard

    welcome_label = ctk.CTkLabel(root, text="Welcome back,", font=("Bahnschrift SemiCondensed", 26),text_color="black", bg_color="white")
    frame1 = ctk.CTkFrame(root, width=400, height=100, fg_color="lightblue", corner_radius=10)
    text_label = ctk.CTkLabel(frame1, text="       There is no pending Donations       ", text_color="black")
    status_label = ctk.CTkLabel(root, text="Donation Status", font=("Bahnschrift SemiCondensed", 26),text_color="black", bg_color="white")
    points_label = ctk.CTkLabel(root, text="0", font=("Arial", 19,"bold"),fg_color = "#00163c",bg_color="#00163c",text_color = "white")
        #profile image

    img = create_circle_image("D:\\Profile Pic\\PIC.jpg", 80)  # Provide the path to your image
    img_tk = ImageTk.PhotoImage(img)

    # label to place the image
    label = tk.Label(root, image=img_tk, borderwidth=0)
    label.place(x=1450, y=20)



    dashboard()

    root.mainloop()

d_main("JD_1","Donor")

```

## mail.py:

```py
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

```

## main.py:

```py
import customtkinter as ctk
from PIL import Image, ImageTk
from customtkinter import CTkImage  # Import CTkImage
from database import login, stop, signup
import re
import time
import threading
from mail import send_email
from sms import send_otp
from donor_dash import d_main,image
import tkinter as tk

password_visible = False
timer_duration = 80  # 5 minutes in seconds
otp = None
timer_running = False
otp_valid = False
email = ""
flag = 1
phone = ""
phone_otp_sent = False
stop_thread = False
organization_name = ""
org_type = ""
location = ""
state = ""
district = ""
zip_code = 0


root = ctk.CTk()

india_districts = {
    "Select State": ["Select District"],
    "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", "Prakasam", "Srikakulam", "Sri Potti Sriramulu Nellore", "Visakhapatnam", "Vizianagaram", "West Godavari", "YSR Kadapa"],
    "Arunachal Pradesh": ["Anjaw", "Changlang", "Dibang Valley", "East Kameng", "East Siang", "Kamle", "Kra Daadi", "Kurung Kumey", "Lepa Rada", "Lohit", "Longding", "Lower Dibang Valley", "Lower Siang", "Lower Subansiri", "Namsai", "Pakke Kessang", "Papum Pare", "Shi Yomi", "Siang", "Tawang", "Tirap", "Upper Dibang Valley", "Upper Siang", "Upper Subansiri", "West Kameng", "West Siang"],
    "Assam": ["Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh", "Dima Hasao", "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat", "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Karimganj", "Kokrajhar", "Lakhimpur", "Majuli", "Morigaon", "Nagaon", "Nalbari", "Sivasagar", "Sonitpur", "South Salmara-Mankachar", "Tinsukia", "Udalguri", "West Karbi Anglong"],
    "Bihar": ["Araria", "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur", "Bhojpur", "Buxar", "Darbhanga", "East Champaran", "Gaya", "Gopalganj", "Jamui", "Jehanabad", "Kaimur", "Katihar", "Khagaria", "Kishanganj", "Lakhisarai", "Madhepura", "Madhubani", "Munger", "Muzaffarpur", "Nalanda", "Nawada", "Patna", "Purnia", "Rohtas", "Saharsa", "Samastipur", "Saran", "Sheikhpura", "Sheohar", "Sitamarhi", "Siwan", "Supaul", "Vaishali", "West Champaran"],
    "Chhattisgarh": ["Balod", "Baloda Bazar", "Balrampur", "Bastar", "Bemetara", "Bijapur", "Bilaspur", "Dantewada", "Dhamtari", "Durg", "Gariaband", "Gaurela-Pendra-Marwahi", "Janjgir-Champa", "Jashpur", "Kabirdham", "Kanker", "Kondagaon", "Korba", "Koriya", "Mahasamund", "Mungeli", "Narayanpur", "Raigarh", "Raipur", "Rajnandgaon", "Sukma", "Surajpur", "Surguja"],
    "Goa": ["North Goa", "South Goa"],
    "Gujarat": ["Ahmedabad", "Amreli", "Anand", "Aravalli", "Banaskantha", "Bharuch", "Bhavnagar", "Botad", "Chhota Udaipur", "Dahod", "Dang", "Devbhoomi Dwarka", "Gandhinagar", "Gir Somnath", "Jamnagar", "Junagadh", "Kheda", "Kutch", "Mahisagar", "Mehsana", "Morbi", "Narmada", "Navsari", "Panchmahal", "Patan", "Porbandar", "Rajkot", "Sabarkantha", "Surat", "Surendranagar", "Tapi", "Vadodara", "Valsad"],
    "Haryana": ["Ambala", "Bhiwani", "Charkhi Dadri", "Faridabad", "Fatehabad", "Gurugram", "Hisar", "Jhajjar", "Jind", "Kaithal", "Karnal", "Kurukshetra", "Mahendragarh", "Nuh", "Palwal", "Panchkula", "Panipat", "Rewari", "Rohtak", "Sirsa", "Sonipat", "Yamunanagar"],
    "Himachal Pradesh": ["Bilaspur", "Chamba", "Hamirpur", "Kangra", "Kinnaur", "Kullu", "Lahaul and Spiti", "Mandi", "Shimla", "Sirmaur", "Solan", "Una"],
    "Jharkhand": ["Bokaro", "Chatra", "Deoghar", "Dhanbad", "Dumka", "East Singhbhum", "Garhwa", "Giridih", "Godda", "Gumla", "Hazaribagh", "Jamtara", "Khunti", "Koderma", "Latehar", "Lohardaga", "Pakur", "Palamu", "Ramgarh", "Ranchi", "Sahebganj", "Seraikela Kharsawan", "Simdega", "West Singhbhum"],
    "Karnataka": ["Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban", "Bidar", "Chamarajanagar", "Chikballapur", "Chikkamagaluru", "Chitradurga", "Dakshina Kannada", "Davanagere", "Dharwad", "Gadag", "Hassan", "Haveri", "Kalaburagi", "Kodagu", "Kolar", "Koppal", "Mandya", "Mysuru", "Raichur", "Ramanagara", "Shivamogga", "Tumakuru", "Udupi", "Uttara Kannada", "Vijayapura", "Yadgir"],
    "Kerala": ["Alappuzha", "Ernakulam", "Idukki", "Kannur", "Kasaragod", "Kollam", "Kottayam", "Kozhikode", "Malappuram", "Palakkad", "Pathanamthitta", "Thiruvananthapuram", "Thrissur", "Wayanad"],
    "Madhya Pradesh": ["Agar Malwa", "Alirajpur", "Anuppur", "Ashoknagar", "Balaghat", "Barwani", "Betul", "Bhind", "Bhopal", "Burhanpur", "Chhatarpur", "Chhindwara", "Damoh", "Datia", "Dewas", "Dhar", "Dindori", "Guna", "Gwalior", "Harda", "Hoshangabad", "Indore", "Jabalpur", "Jhabua", "Katni", "Khandwa", "Khargone", "Mandla", "Mandsaur", "Morena", "Narsinghpur", "Neemuch", "Niwari", "Panna", "Raisen", "Rajgarh", "Ratlam", "Rewa", "Sagar", "Satna", "Sehore", "Seoni", "Shahdol", "Shajapur", "Sheopur", "Shivpuri", "Sidhi", "Singrauli", "Tikamgarh", "Ujjain", "Umaria", "Vidisha"],
    "Maharashtra": ["Ahmednagar", "Akola", "Amravati", "Aurangabad", "Beed", "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur", "Latur", "Mumbai City", "Mumbai Suburban", "Nagpur", "Nanded", "Nandurbar", "Nashik", "Osmanabad", "Palghar", "Parbhani", "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"],
    "Manipur": ["Bishnupur", "Chandel", "Churachandpur", "Imphal East", "Imphal West", "Jiribam", "Kakching", "Kamjong", "Kangpokpi", "Noney", "Pherzawl", "Senapati", "Tamenglong", "Tengnoupal", "Thoubal", "Ukhrul"],
    "Meghalaya": ["East Garo Hills", "East Jaintia Hills", "East Khasi Hills", "North Garo Hills", "Ri Bhoi", "South Garo Hills", "South West Garo Hills", "South West Khasi Hills", "West Garo Hills", "West Jaintia Hills", "West Khasi Hills"],
    "Mizoram": ["Aizawl", "Champhai", "Hnahthial", "Khawzawl", "Kolasib", "Lawngtlai", "Lunglei", "Mamit", "Saiha", "Saitual", "Serchhip"],
    "Nagaland": ["Chumoukedima", "Dimapur", "Kiphire", "Kohima", "Longleng", "Mokokchung", "Mon", "Noklak", "Peren", "Phek", "Tuensang", "Wokha", "Zunheboto"],
    "Odisha": ["Angul", "Balangir", "Balasore", "Bargarh", "Bhadrak", "Boudh", "Cuttack", "Deogarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghpur", "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal", "Kendrapara", "Kendujhar", "Khordha", "Koraput", "Malkangiri", "Mayurbhanj", "Nabarangpur", "Nayagarh", "Nuapada", "Puri", "Rayagada", "Sambalpur", "Sonepur", "Sundargarh"],
    "Punjab": ["Amritsar", "Barnala", "Bathinda", "Faridkot", "Fatehgarh Sahib", "Fazilka", "Ferozepur", "Gurdaspur", "Hoshiarpur", "Jalandhar", "Kapurthala", "Ludhiana", "Mansa", "Moga", "Muktsar", "Nawanshahr", "Pathankot", "Patiala", "Rupnagar", "Sangrur", "SAS Nagar", "Sri Muktsar Sahib", "Tarn Taran"],
    "Rajasthan": ["Ajmer", "Alwar", "Banswara", "Baran", "Barmer", "Bharatpur", "Bhilwara", "Bikaner", "Bundi", "Chittorgarh", "Churu", "Dausa", "Dholpur", "Dungarpur", "Hanumangarh", "Jaipur", "Jaisalmer", "Jalore", "Jhalawar", "Jhunjhunu", "Jodhpur", "Karauli", "Kota", "Nagaur", "Pali", "Pratapgarh", "Rajsamand", "Sawai Madhopur", "Sikar", "Sirohi", "Sri Ganganagar", "Tonk", "Udaipur"],
    "Sikkim": ["East Sikkim", "North Sikkim", "South Sikkim", "West Sikkim"],
    "Tamil Nadu": ["Ariyalur", "Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", "Dindigul", "Erode", "Kanchipuram", "Kanniyakumari", "Karur", "Krishnagiri", "Madurai", "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai", "Ramanathapuram", "Salem", "Sivaganga", "Thanjavur", "Theni", "Tiruchirappalli", "Tirunelveli", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Vellore", "Villupuram", "Virudhunagar", "Thoothukudi", "Kanyakumari", "Tiruvarur", "Dindigul", "Chengalpattu", "Kallakurichi", "Ranipet", "Vellore"],
    "Telangana": ["Adilabad", "Bhadradri Kothagudem", "Hyderabad", "Jagtial", "Jangaon", "Jayashankar Bhupalpally", "Jogulamba Gadwal", "Kamareddy", "Karimnagar", "Khammam", "Kumuram Bheem Asifabad", "Mahabubabad", "Mahabubnagar", "Mancherial", "Medak", "Medchal-Malkajgiri", "Mulugu", "Nagarkurnool", "Nalgonda", "Narayanpet", "Nirmal", "Nizamabad", "Peddapalli", "Rajanna Sircilla", "Rangareddy", "Sangareddy", "Siddipet", "Suryapet", "Vikarabad", "Wanaparthy", "Warangal Rural", "Warangal Urban", "Yadadri Bhuvanagiri"],
    "Tripura": ["Dhalai", "Gomati", "Khowai", "North Tripura", "Sepahijala", "South Tripura", "Unakoti", "West Tripura"],
    "Uttar Pradesh": ["Agra", "Aligarh", "Ambedkar Nagar", "Amethi", "Amroha", "Auraiya", "Ayodhya", "Azamgarh", "Badaun", "Baghpat", "Bahraich", "Ballia", "Balrampur", "Banda", "Barabanki", "Bareilly", "Basti", "Bhadohi", "Bijnor", "Budaun", "Bulandshahr", "Chandauli", "Chitrakoot", "Deoria", "Etah", "Etawah", "Farrukhabad", "Fatehpur", "Firozabad", "Gautam Buddha Nagar", "Ghaziabad", "Ghazipur", "Gonda", "Gorakhpur", "Hamirpur", "Hapur", "Hardoi", "Hathras", "Jalaun", "Jaunpur", "Jhansi", "Kannauj", "Kanpur Dehat", "Kanpur Nagar", "Kasganj", "Kaushambi", "Kheri", "Kushinagar", "Lalitpur", "Lucknow", "Maharajganj", "Mahoba", "Mainpuri", "Mathura", "Mau", "Meerut", "Mirzapur", "Moradabad", "Muzaffarnagar", "Pilibhit", "Pratapgarh", "Prayagraj", "Raebareli", "Rampur", "Saharanpur", "Sambhal", "Sant Kabir Nagar", "Shahjahanpur", "Shamli", "Shrawasti", "Siddharthnagar", "Sitapur", "Sonbhadra", "Sultanpur", "Unnao", "Varanasi"],
    "Uttarakhand": ["Almora", "Bageshwar", "Chamoli", "Champawat", "Dehradun", "Haridwar", "Nainital", "Pauri Garhwal", "Pithoragarh", "Rudraprayag", "Tehri Garhwal", "Udham Singh Nagar", "Uttarkashi"],
    "West Bengal": ["Alipurduar", "Bankura", "Birbhum", "Cooch Behar", "Dakshin Dinajpur", "Darjeeling", "Hooghly", "Howrah", "Jalpaiguri", "Jhargram", "Kalimpong", "Kolkata", "Malda", "Murshidabad", "Nadia", "North 24 Parganas", "Paschim Bardhaman", "Paschim Medinipur", "Purba Bardhaman", "Purba Medinipur", "Purulia", "South 24 Parganas", "Uttar Dinajpur"],
    "Andaman and Nicobar Islands": ["Nicobar", "North and Middle Andaman", "South Andaman"],
    "Chandigarh": ["Chandigarh"],
    "Dadra and Nagar Haveli and Daman and Diu": ["Dadra and Nagar Haveli", "Daman", "Diu"],
    "Lakshadweep": ["Lakshadweep"],
    "Delhi": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "North East Delhi", "North West Delhi", "Shahdara", "South Delhi", "South East Delhi", "South West Delhi", "West Delhi"],
    "Puducherry": ["Karaikal", "Mahe", "Puducherry", "Yanam"]
}

def main():
    # Create the main window
    ctk.set_appearance_mode("light")  # Can switch to "dark"
    # root = ctk.CTk()
    root.geometry("1980x1080")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 1480
    window_height = 840
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Initialize imagec
    image_path = "D:/atest.jpg"
    image = Image.open(image_path)

    # #use this small image for login page as it is suited for that


    # Create a canvas to display the image as the background
    canvas = ctk.CTkCanvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight())
    canvas.pack(fill="both", expand=True)

    # Create a frame to hold the text
    # left_frame = ctk.CTkFrame(root, width=750, height=500, fg_color="lightblue", corner_radius=0)
    # # left_frame.pack(side="left")
    # left_frame.place(relx=0.05, rely=0.1, relwidth=0.7, relheight=0.8)
    #
    # # Add a label to the frame with your desired text
    # label = ctk.CTkLabel(left_frame, text="Your text here", font=("Arial", 20))
    # label.pack(padx=20, pady=20)

    # Function to display the image
    def display_image():
        resized_image = image.resize((root.winfo_width(), root.winfo_height()), Image.LANCZOS)
        image_tk = ImageTk.PhotoImage(resized_image)
        canvas.create_image(0, 0, image=image_tk, anchor="nw")
        canvas.image = image_tk  # Keep a reference to avoid garbage collection

    # Display the initial image
    display_image()



    # Function to handle resize events
    def on_resize(event):
        canvas.config(width=event.width, height=event.height)
        display_image()
        # display_small_image()

    # Bind the resize event to the resize function
    root.bind("<Configure>", on_resize)

    home_page()
    # Start the application
    root.mainloop()



def home_page():
    global email,otp

    def start_timer():
        global timer_running, otp_valid
        timer_running = True
        time_remaining = 180  # OTP is valid for 60 seconds

        while time_remaining > 0:
            if stop_thread :
                break
            elif not stop_thread :
                time.sleep(1)
                time_remaining -= 1
                timer_label.configure(text=f"Time remaining: {time_remaining} seconds")

        otp_valid = False  # Invalidate the OTP after 60 seconds
        timer_running = False
        # timer_label.configure(text="OTP expired. Please request a new one.")

    # def start_timer(timer_label):
    #     timer_running = True
    #     remaining_time = timer_duration
    #
    #     def countdown():
    #         global timer_running
    #         nonlocal remaining_time
    #         if remaining_time > 0 and timer_running:
    #             mins, secs = divmod(remaining_time, 60)
    #             time_format = '{:02d}:{:02d}'.format(mins, secs)
    #             timer_label.configure(text=f"Time Remaining: {time_format}")
    #             remaining_time -= 1
    #             timer_label.after(1000, countdown)  # Schedule next countdown after 1 second
    #         else:
    #             timer_running = False
    #             timer_label.configure(text="Didn't receive the mail?")
    #             submit_button.configure(state="disabled")  # Disable the submit button
    #
    #     countdown()  # Start the countdown
    def ph_otp(otp_entry,timer_label):
        global timer_running, otp, phone_otp_sent, phone_verification,phone,stop_thread,organization_name,org_type,email,location,state,district,zip_code

        entered_otp = otp_entry.get()

        if int(entered_otp) == otp :  # Phone verification stage
            print("Phone OTP Verified")

            stop_thread = True
            timer_running = False  # Stop the timer
            timer_label.place_forget()
            invalid_otp_label.place_forget()
            success_label.configure(text="Both email and phone verified!", text_color="green")
            success_label.place(x=1177, y=260)
            print(organization_name,org_type)
            signup(organization_name,org_type, email, phone, location,district,state,int(zip_code))
            # Handle the next step after phone verification is complete
            # For example, moving to the next screen or completing registration
        else :
            invalid_otp_label.configure(text = "Invalid OTP entered")
            invalid_otp_label.place(x=1204, y=280)


    def verify_otp(otp_entry, timer_label):
        global timer_running, otp, phone_otp_sent, phone_verification,phone,stop_thread

        if not timer_running:  # Check if the timer is still running
            return
        entered_otp = otp_entry.get()

        if entered_otp.isdigit() and int(entered_otp) == otp:
            if not phone_otp_sent:  # Email verification stage
                stop_thread = True
                timer_running = False  # Stop the timer
                timer_label.place_forget()
                invalid_otp_label.place_forget()


                  # Stop the timer

                # Generate and send OTP to phone for phone number verification
                otp = send_otp(phone)

                time.sleep(2)# Generate a new OTP for phone verification
                stop_thread = False
                timer_running = True
                phone_otp_sent = True  # Mark that phone OTP is sent

                # Update labels for phone number verification
                email_verify_label.configure(text="Phone no. verification")
                verify_text_lablel.configure(
                    text="We just sent you the OTP on your number, please \nenter it below to verify your number."
                )
                invalid_otp_label.place_forget()
                email_verify_label.place(x=1180, y=120)
                verify_text_lablel.place(x=1123, y=170)
                otp_entry.delete(0, 'end')  # Clear the entry field for new OTP
                otp_entry.place(x=1200, y=230)
                timer_label.place(x=1174, y=260)
                submit1_button.place(x=1192, y=310)

            # elif phone_otp_sent :  # Phone verification stage
            #     print("Phone OTP Verified")
            #     timer_label.place_forget()
            #     invalid_otp_label.place_forget()
            #     timer_running = False  # Stop the timer
            #     timer_label.configure(text="Phone no. verified successfully", text_color="green")
            #     timer_label.place(x=1192, y=260)
            #
            #     # Handle the next step after phone verification is complete
            #     # For example, moving to the next screen or completing registration
            #     print("Both email and phone verified!")

        else:
            print("Invalid OTP")
            invalid_otp_label.configure(text = "Invalid OTP entered")
            invalid_otp_label.place(x=1204, y=280)

    def is_valid_email(email):
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_pattern, email)

    def is_valid_phone(phone):
        return phone.isdigit() and len(phone) == 10

    def is_valid_zip(zip_code):
        return zip_code.isdigit() and len(zip_code) == 6
    def login_info():
        submit1_button.place_forget()
        invalid_otp_label.place_forget()
        success_label.place_forget()
        user_id = user_id_entry.get()
        password = password_entry.get()
        valid = True

        # Reset error labels
        user_id_error_label.configure(text="")
        password_error_label.configure(text="")
        success_label.configure(text="")

        if not user_id:
            user_id_error_label.configure(text="User ID is required", text_color="red", font=("Helvetica", 12),bg_color="white",fg_color="white",width=0,corner_radius=0)
            user_id_error_label.place(x=1136, y=198)
            valid = False

        if not password:

            password_error_label.configure(text="Password is required", text_color="red", font=("Helvetica", 12),bg_color="white",fg_color="white",width=0,corner_radius=0)
            show_password_label.place_forget()
            eye_button.place_forget()
            eye_button.place(x=1125, y=308)
            show_password_label.place(x=1160, y=314)
            password_error_label.place(x=1136, y=288)
            valid = False

        if valid:

            chk,organiz_type = login(user_id, password)
            if chk == 1:
                print("login success")
                success_label.place(x=1134,y=378)
                success_label.configure(text="Login Successful !", text_color="green",font=("Helvetica", 13),bg_color="white",fg_color="white",width=0,corner_radius=0)
                # root.after(2000,root.destroy)
                root.destroy()
                d_main(user_id,organiz_type)

            else:
                success_label.place(x=1134, y=378)
                success_label.configure(text="Wrong credentials entered !", text_color="red",font=("Helvetica", 13),bg_color="white",fg_color="white",width=0,corner_radius=0)

    def sign_up_info():
        global email,otp,phone,timer_running,organization_name,org_type,location,state,district,zip_code

        organization_name = organization_name_entry.get()
        org_type = combobox_var.get()  # Get the selected type
        email = email_entry.get()
        phone = phone_entry.get()
        location = location_street_entry.get()
        state = combobox1.get()
        district = combobox2.get()
        zip_code=zip_entry.get()

        valid = True

        # Reset error labels
        organization_name_error_label.configure(text="")
        email_error_label.configure(text="")
        phone_error_label.configure(text="")
        location_street_id_error_label.configure(text="")
        success_label.configure(text="")

        if not organization_name:
            organization_name_error_label.configure(text="Organization name is required", text_color="red",
                                                    font=("Helvetica", 12,),fg_color="white",bg_color="white",width=0)
            organization_name_error_label.place(x=954, y=198)
            valid = False

        if not email:
            email_error_label.configure(text="Email ID is required", text_color="red", font=("Helvetica", 12),bg_color="white",fg_color="white",width=0)
            email_error_label.place(x=954, y=278)
            valid = False
        elif not is_valid_email(email):
            email_error_label.configure(text="Invalid email format", text_color="red", font=("Helvetica", 12),bg_color="white",fg_color="white",width=0)
            email_error_label.place(x=954, y=278)
            valid = False

        if not phone:
            phone_error_label.configure(text="Phone number is required", text_color="red", font=("Helvetica", 12),bg_color="white",fg_color="white",width=0)
            phone_error_label.place(x=1250, y=278)
            valid = False
        elif not is_valid_phone(phone):
            phone_error_label.configure(text="Phone number must be 10 digits", text_color="red", font=("Helvetica", 12),bg_color="white",fg_color="white",width=0)
            phone_error_label.place(x=1250, y=278)
            valid = False

        if not location:
            location_street_id_error_label.configure(text="Location is required", text_color="red",
                                                     font=("Helvetica", 12),fg_color="white",bg_color="white",width=0)
            location_street_id_error_label.place(x=954, y=358)
            valid = False

        if not zip_code:
            zip_error_label.configure(text="Zip Code is required", text_color="red",
                                                     font=("Helvetica", 12),fg_color="white",bg_color="white",width=0)
            zip_error_label.place(x=1250, y=358)
            valid = False
        elif not is_valid_zip(zip_code) :
            zip_error_label.configure(text="Please enter correct pin code", text_color="red",
                                      font=("Helvetica", 12), fg_color="white", bg_color="white", width=0)
            zip_error_label.place(x=1250, y=358)
            valid = False

        if valid:
            organization_name_label.place_forget()
            organization_name_entry.place_forget()
            organization_name_error_label.place_forget()
            organization_type_label.place_forget()
            combobox1.place_forget()
            combobox2.place_forget()
            combobox2.place_forget()
            email_label.place_forget()
            email_entry.place_forget()
            email_error_label.place_forget()
            phone_label.place_forget()
            phone_entry.place_forget()
            phone_error_label.place_forget()
            location_label.place_forget()
            location_street_entry.place_forget()
            location_street_id_error_label.place_forget()
            zip_label.place_forget()
            zip_entry.place_forget()
            zip_error_label.place_forget()
            state_label.place_forget()
            dis_label.place_forget()
            combobox.place_forget()
            next_button.place_forget()


            # threading.Thread(target=start_timer, args=(timer_label,), daemon=True).start()
            email_verify_label.place(x=1200, y=120)
            verify_text_lablel.place(x=1123, y=170)
            otp_entry.place(x=1200, y=230)
            timer_label.place(x=1174, y=260)
            submit_button.place(x=1192, y=310)

            otp = send_email(email)

            threading.Thread(target=start_timer).start()
            """signup(organization_name, type, email, phone, location)
            success_label.place(x=112, y=545)
            success_label.configure(text="Registration successful !", text_color="green",
                                    font=("Helvetica", 11, "bold"))"""

    def combobox_callback(choice):

        return choice.lower()

    def cm_callback(state):
        combobox2 = ctk.CTkComboBox(root, values=india_districts[state])
        # combobox2.place(x=1250,y=410)

        return state.lower()

    def toggle_password_visibility():
        global password_visible
        if password_visible:
            password_entry.configure(show="•")  # Mask the password
            eye_button.configure(image=eye_image_off)
            password_visible = False
        else:
            password_entry.configure(show="")  # Show the actual password
            eye_button.configure(image=eye_image_on)
            # Change to on image
            password_visible = True

    def sign_in_active():
        organization_name_label.place_forget()
        organization_name_entry.place_forget()
        organization_name_error_label.place_forget()
        organization_type_label.place_forget()
        combobox1.place_forget()
        combobox2.place_forget()
        email_label.place_forget()
        email_entry.place_forget()
        email_error_label.place_forget()
        phone_label.place_forget()
        phone_entry.place_forget()
        phone_error_label.place_forget()
        location_label.place_forget()
        location_street_entry.place_forget()
        location_street_id_error_label.place_forget()
        zip_label.place_forget()
        zip_entry.place_forget()
        zip_error_label.place_forget()
        state_label.place_forget()
        dis_label.place_forget()
        combobox.place_forget()
        next_button.place_forget()
        email_verify_label.place_forget()
        verify_text_lablel.place_forget()
        otp_entry.place_forget()
        submit_button.place_forget()
        timer_label.place_forget()
        submit1_button.place_forget()
        invalid_otp_label.place_forget()
        success_label.place_forget()

        sign_in_button.configure(root, text="Sign in", width=0, fg_color="white", text_color="blue",bg_color="white",
                                   hover_color="white", border_width=0, border_color="white", corner_radius=0,
                                   font=("Helvetica", 16))
        register_button.configure(root, text="Register", width=0, fg_color="white", text_color="black",bg_color="white",
                                    hover_color="white", border_width=0, border_color="white",
                                    corner_radius=0, font=("Helvetica", 16))
        user_id_label.place(x=1134,y=140)
        user_id_entry.place(x=1134,y=170)

        password_label.place(x=1134,y=230)
        password_entry.place(x=1134,y=260)

        eye_button.place(x=1125,y=288)
        show_password_label.place(x=1160,y=294)
        login_button.place(x=1134,y=344)
        logo_label.place(x=150,y=30)
        tagline.place(x=500, y=190)

    def register_active():

        user_id_label.place_forget()
        user_id_entry.place_forget()
        password_label.place_forget()
        password_entry.place_forget()
        user_id_error_label.place_forget()
        password_error_label.place_forget()
        eye_button.place_forget()
        show_password_label.place_forget()
        login_button.place_forget()
        success_label.place_forget()
        email_verify_label.place_forget()
        verify_text_lablel.place_forget()
        otp_entry.place_forget()
        submit_button.place_forget()
        timer_label.place_forget()
        submit1_button.place_forget()
        tagline.place_forget()
        register_button.configure(root, text="Register", width=0, fg_color="white", text_color="blue",
                                  bg_color="white",
                                  hover_color="white", border_width=0, border_color="white",
                                  corner_radius=0, font=("Helvetica", 16))
        sign_in_button.configure(root, text="Sign in", width=0, fg_color="white", text_color="black", bg_color="white",
                                 hover_color="white", border_width=0, border_color="white", corner_radius=0,
                                 font=("Helvetica", 16))

        organization_name_label.place(x=954,y=140)
        organization_name_entry.place(x=954,y=170)

        organization_type_label.place(x=1250,y=140)
        combobox.place(x=1250,y=170)

        email_label.place(x=954,y=220)
        email_entry.place(x=954,y=250)

        phone_label.place(x=1250,y=220)
        phone_entry.place(x=1250,y=250)

        location_label.place(x=954,y=300)
        location_street_entry.place(x=954,y=330)

        zip_label.place(x=1250,y=300)
        zip_entry.place(x=1250,y=330)

        state_label.place(x=954,y=380)
        combobox1.place(x=954,y=410)

        dis_label.place(x=1250,y=380)
        combobox2.place(x=1250,y=410)

        next_button.place(x=1350,y=490)

    sign_in_button = ctk.CTkButton(root, text="Sign in", width=0, fg_color="white", text_color="blue",bg_color="white",
                                   hover_color="white", border_width=0, border_color="white", corner_radius=0,
                                   font=("Helvetica", 16), command=sign_in_active)
    sign_in_button.place(x=1193, y=15)

    register_button = ctk.CTkButton(root, text="Register", width=0, fg_color="white", text_color="blue",bg_color="white",
                                    hover_color="white", border_width=0, border_color="white",corner_radius=0,
                                    font=("Helvetica", 16),command=register_active)
    register_button.place(x=1285, y=15)

    tagline = ctk.CTkLabel(root, text="Turning excess into abundance, one meal at a time,\nTogether, we’ll turn hunger into hope.",
                        font=("Roboto", 18,"italic","bold"),
                        text_color="orange",bg_color="white",fg_color="white")

    next_button = ctk.CTkButton(root, text="Next >", width=0, fg_color="white",text_color="blue",hover_color="white", command=sign_up_info,font=("Helvetica", 15),bg_color="white")

    # resend_otp_button = ctk.CTkButton(root, text="Resend OTP", width=0, fg_color="white",text_color="blue",hover_color="white", command=resend_otp(email),font=("Helvetica", 13),bg_color="white")

    user_id_label = ctk.CTkLabel(root, text="User ID", font=("Helvetica", 13, "bold"), text_color="black",bg_color="white")
    user_id_entry = ctk.CTkEntry(root, placeholder_text="Enter your user ID", width=260,bg_color="white",fg_color="white")
    user_id_error_label = ctk.CTkLabel(root, text="", font=("Helvetica", 10))

    password_label = ctk.CTkLabel(root, text="Password", font=("Helvetica", 13, "bold"), text_color="black",bg_color="white")
    password_entry = ctk.CTkEntry(root, placeholder_text="Enter your password", width=260, show="•",bg_color="white",fg_color="white")
    password_error_label = ctk.CTkLabel(root, text="", font=("Helvetica", 10))

    eye_image_off = Image.open("D:/square.png")  # Image for password masked
    eye_image_on = Image.open("D:/check_box.png")  # Image for password visible

    # Convert images to CTkImage
    eye_image_off = CTkImage(eye_image_off, size=(30, 30))  # Resize if needed
    eye_image_on = CTkImage(eye_image_on, size=(30, 30))  # Resize if needed

    # Create a label to display the eye image
    eye_button = ctk.CTkButton(root, image=eye_image_off, command=toggle_password_visibility,
                               border_width=0, fg_color="white", hover_color="white",text="",
                               corner_radius=0,width=0,bg_color="white")
    # eye_image_label.bind("<Button-1>", lambda e: toggle_password_visibility())  # Bind click event

    # Create a label to display "Show Password"
    show_password_label = ctk.CTkLabel(root, text="Show Password",text_color="black",fg_color="white",bg_color="white")

    organization_name_label = ctk.CTkLabel(root, text="Organization Name", font=("Helvetica", 13, "bold"), text_color="black",bg_color="white")
    organization_name_entry = ctk.CTkEntry(root, placeholder_text="Enter your organization name", width=240,bg_color="white",fg_color="white")
    organization_name_error_label = ctk.CTkLabel(root, text="", font=("Helvetica", 10))

    organization_type_label = ctk.CTkLabel(root, text="Type", font=("Helvetica", 13, "bold"), text_color="black",bg_color="white")

    combobox_var = ctk.StringVar(value="Select Type")
    combobox = ctk.CTkComboBox(root, values=["NGO", "Donor"], variable=combobox_var, command=combobox_callback,bg_color="white",fg_color="white")

    email_label = ctk.CTkLabel(root, text="Email ID", font=("Helvetica", 13, "bold"), text_color="black",bg_color="white")
    email_entry = ctk.CTkEntry(root, placeholder_text="Enter your email ID", width=240,bg_color="white",fg_color="white")
    email_error_label = ctk.CTkLabel(root, text="", font=("Helvetica", 10))

    phone_label = ctk.CTkLabel(root, text="Phone No", font=("Helvetica", 13, "bold"),text_color="black",bg_color="white")
    phone_entry = ctk.CTkEntry(root, placeholder_text="xxxxxxxxxx", width=220,bg_color="white",fg_color="white")
    phone_error_label = ctk.CTkLabel(root, text="", font=("Helvetica", 10))

    location_label = ctk.CTkLabel(root, text="Location", font=("Helvetica", 13, "bold"),text_color="black",bg_color="white")
    location_street_entry = ctk.CTkEntry(root, placeholder_text="Address line 1", width=240,bg_color="white",fg_color="white")
    location_street_id_error_label = ctk.CTkLabel(root, text="", font=("Helvetica", 10))

    zip_label = ctk.CTkLabel(root, text="Zip Code", font=("Helvetica", 13, "bold"), text_color="black",
                                  bg_color="white")
    zip_entry = ctk.CTkEntry(root, placeholder_text="xxx xxx", width=222, bg_color="white",
                                         fg_color="white")
    zip_error_label = ctk.CTkLabel(root, text="", font=("Helvetica", 10))

    dis_label = ctk.CTkLabel(root, text="District", font=("Helvetica", 13, "bold"), text_color="black",
                             bg_color="white")
    combobox_dis = ctk.StringVar(value="Select District")
    combobox2 = ctk.CTkComboBox(root, values=india_districts["Tamil Nadu"], variable=combobox_dis, command=cm_callback("Select State"),bg_color="white",fg_color="white")

    state_label = ctk.CTkLabel(root, text="State", font=("Helvetica", 13, "bold"), text_color="black",
                             bg_color="white")
    combobox_state = ctk.StringVar(value="Select State")
    combobox1 = ctk.CTkComboBox(root,
                                values=["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
                                        "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
                                        "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
                                        "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
                                        "Uttar Pradesh", "Uttarakhand", "West Bengal"], variable=combobox_state,
                                command=cm_callback,fg_color="white",bg_color="white")


    email_verify_label = ctk.CTkLabel(root, text="Verify your email", font=("Helvetica", 15, "bold"), text_color="black",
                             bg_color="white")
    verify_text_lablel = ctk.CTkLabel(root, text="We just sent you the OTP on your \nemail,please enter it below to verify your email.", font=("Helvetica", 14), text_color="black",
                             bg_color="white")
    otp_entry = ctk.CTkEntry(root, placeholder_text="x x x x", width=122, bg_color="white",
                 fg_color="white")
    submit_button = ctk.CTkButton(root, text="Submit", width=150,fg_color="blue",command=lambda: verify_otp(otp_entry, timer_label))
    submit1_button = ctk.CTkButton(root, text="Submit", width=150,fg_color="blue",command=lambda: ph_otp(otp_entry, timer_label))

    timer_label = ctk.CTkLabel(root, text="Time Remaining: 80",bg_color="white",fg_color="white",width=0)
    # threading.Thread(target=start_timer, args=(timer_label,), daemon=True).start()
    invalid_otp_label = ctk.CTkLabel(root, text="Invalid OTP entered", bg_color="white", fg_color="white", width=0,
                                     text_color="red")

    # Start the timer in a new thread
    login_button = ctk.CTkButton(root, text="Sign In", width=260, fg_color="blue",command = login_info)

    success_label = ctk.CTkLabel(root, text="", bg_color="white", fg_color="white", width=0)
    logo_label = ctk.CTkLabel(root, text="FoodFuel", font=("Poppins", 36, "bold"), text_color="black",
                               bg_color="white")
    sign_in_active()


if __name__ == "__main__":
    main()

```

## sms.py:

```py
from twilio.rest import Client
import random

from mail import send_email

# Your Twilio account SID and Auth Token from www.twilio.com/console
account_sid = 'AC46428ac71460e85fb3cd32448a4316c0'
auth_token = '6bae0f55a0043b649b7dc4ee8a589824'

# Create a Twilio client
client = Client(account_sid, auth_token)

# Function to generate a random OTP
def generate_otp():
    return random.randint(1000, 9999)
number = '+91'
# Function to send the OTP
def send_otp(phone_number):
    global number
    otp = generate_otp()
    number = number +phone_number
    message = client.messages.create(
        body=f"Your OTP is {otp}",
        from_='+18507833937',  # Your Twilio number
        to=number                # Recipient's phone number
    )
    print(f"OTP sent: {otp}")
    return otp

# Example usage: sending OTP to a phone number


```
