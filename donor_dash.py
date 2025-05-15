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
