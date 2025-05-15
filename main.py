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
