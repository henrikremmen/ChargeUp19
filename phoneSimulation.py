import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
from PIL import Image, ImageTk
from client import MQTTClient
from client import BasicClient
from time import sleep
import json
import stmpy
from stmpy import Machine, Driver


class ChargeUpApp:
    
    def __init__(self, initial_battery, ip):
        """Charge app, global variabels defined below. They don't reset"""
        self.ipAdress = ip
        self.root = tk.Tk()
        self.root.title("ChargeUp!")
        self.root.geometry("300x500")  # Larger window size
        self.current_screen = None
        self.username = ""
        self.password = ""
        self.httpClient = BasicClient(ip)
        self.mqttClient = MQTTClient()
        self.token = None  
        self.initial_battery = initial_battery
        self.initial_cost = 0
        self.cancel = False

        self.create_state_machine()

        # Initialize screens
        self.login_screen()
        
        self.root.mainloop()


    def create_state_machine(self):
        """Create the State Machine instance"""
        # Define your transitions here
        
        # State machine
        t0 = {"source": "initial", 
              "target": "login"}

        t1 = {"trigger": "LB", 
              "source": "login",
              "target": "station",
              "effect": "choose_station_screen"}

        t2 = {"trigger": "EX", 
              "source": "station",
              "target": "login",
              "effect": "reset_and_goto_login"}

        t3 = {"trigger": "SB", 
              "source": "station",
              "target": "charge",
              "effect": "charging_screen"}

        t4 = {"trigger": "CB", 
              "source": "charge",
              "target": "charge",}

        t5 = {"trigger": "PB", 
              "source": "charge",
              "target": "login",
              "effect": "reset_and_goto_login"}

        machine = Machine(name='chargeUp', transitions=[t0, t1, t2, t3, t4, t5], obj=self)
        self.stm = machine

        driver = Driver()
        driver.add_machine(self.stm)

        driver.start()
    

    def login_screen(self):
        """Login screen, username and passoword"""
        self.clear_screen()
        self.current_screen = "login"
        
        # Create widgets
        # Load and display the logo
        logo_img = Image.open("./logo.webp")  
        logo_img = logo_img.resize((170, 170))  # Resize image
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(self.root, image=logo_photo)
        logo_label.image = logo_photo  # Keep a reference to prevent garbage collection
        logo_label.pack(pady=20)
        
        username_label = tk.Label(self.root, text="Username:", font=("Arial", 16))
        username_label.pack()
        self.username_entry = tk.Entry(self.root, font=("Arial", 16))
        self.username_entry.pack(pady=10) 
        
        password_label = tk.Label(self.root, text="Password:", font=("Arial", 16))
        password_label.pack()
        self.password_entry = tk.Entry(self.root, show="*", font=("Arial", 16))
        self.password_entry.pack(pady=10)  
        
        login_button = tk.Button(self.root, text="Login", command=self.login_logic, font=("Arial", 16))
        login_button.pack(pady=20)


    def login_logic(self):
        """Runs right after login in, tries to sign in user with the server"""
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        print("Username:", self.username)
        print("Password:", self.password)

        sign_in_data = {"type": "sign_in", "username": self.username, "password": self.password}
        
        try:
            response = self.send_custom_post_request(sign_in_data)
            response = response.json()
            self.token = response["token"]
            print("token value is " + str(self.token))
            self.stm.send('LB')
            #self.choose_station_screen()
        except:
            print("Wrong credentials")
            messagebox.showinfo("Payment", "Wrong username or password")
            self.reset_and_goto_login()
    

    def choose_station_screen(self):
        """Station choosing screen, with visual-only dropdown for choosing a station."""
        self.clear_screen()
        self.current_screen = "choose_station"

        # Create widgets
        label = tk.Label(self.root, text="Choose Station", font=("Arial", 24), pady=20)
        label.pack()

        # Dropdown for choosing stations
        stations = ['Station 1']
        self.station_var = tk.StringVar()
        self.station_var.set(stations[0])  # Default value
        station_dropdown = ttk.Combobox(self.root, textvariable=self.station_var, values=stations, font=("Arial", 16))
        station_dropdown.pack(pady=10)

        # Request button that triggers state transition directly
        request_button = tk.Button(self.root, text="Request", command=self.request_station, font=("Arial", 16))
        request_button.pack(pady=20)

        print("Request button pressed")  # Print to console when button pressed

    def request_station(self):
        """Function to handle station requests and transition to the charging screen."""
        # Transition directly to the charging screen
        self.stm.send('SB')

    

    def charging_screen(self):
        """Charging screen, this is where we send the action messsages to the server"""
        self.clear_screen()

        self.price_var = tk.StringVar(value="0")  # Initialize as StringVar with initial value "0"

        start_action = {"type": "action", "status": "start", "token": self.token, "battery_level": self.initial_battery}

        try:
            response = self.send_custom_post_request(start_action)
            response = response.json()
            print("Response is ", response)
        except:
            print("Wrong credentials")

        try:
            self.current_screen = "charging"

            self.mqttClient.connect()
            self.mqttClient.subscribe("ttm4115/team19/station/" + str(response["info"]["car_id"]) + "/#")
            self.car_id = str(response["info"]["car_id"])
            
            # Create widgets
            label = tk.Label(self.root, text=f"Charging Page", font=("Arial", 24), pady=20)
            label.pack()

            # Charger ID
            charger_id_frame = tk.Frame(self.root)
            charger_id_frame.pack(pady=(0, 10))
            charger_id_label = tk.Label(charger_id_frame, text="Charger ID:", font=("Arial", 16))
            charger_id_label.pack(side=tk.LEFT)
            self.charger_id_var = tk.StringVar(value=response["info"]["charger_id"])
            charger_id_entry = tk.Label(charger_id_frame, textvariable=self.charger_id_var, font=("Arial", 16), pady=5)
            charger_id_entry.pack(side=tk.RIGHT)

            # Car ID
            car_id_frame = tk.Frame(self.root)
            car_id_frame.pack(pady=(0, 10))
            car_id_label = tk.Label(car_id_frame, text="Car ID:", font=("Arial", 16))
            car_id_label.pack(side=tk.LEFT)
            self.car_id_var = tk.StringVar(value=response["info"]["car_id"])
            car_id_entry = tk.Label(car_id_frame, textvariable=self.car_id_var, font=("Arial", 16), pady=5)
            car_id_entry.pack(side=tk.RIGHT)

            # Battery Level
            battery_level_frame = tk.Frame(self.root)
            battery_level_frame.pack(pady=(0, 10))
            battery_level_label = tk.Label(battery_level_frame, text="Battery Level:", font=("Arial", 16))
            battery_level_label.pack(side=tk.LEFT)
            self.battery_level_var = tk.StringVar(value=self.initial_battery)
            battery_level_entry = tk.Label(battery_level_frame, textvariable=self.battery_level_var, font=("Arial", 16), pady=5)
            battery_level_entry.pack(side=tk.RIGHT)

            # Range
            range_frame = tk.Frame(self.root)
            range_frame.pack(pady=(0, 10))
            range_label = tk.Label(range_frame, text="Range:", font=("Arial", 16))
            range_label.pack(side=tk.LEFT)
            self.range_var = tk.StringVar(value=(str(self.initial_battery*2) + " km"))
            range_entry = tk.Label(range_frame, textvariable=self.range_var, font=("Arial", 16), pady=5)
            range_entry.pack(side=tk.RIGHT)

            # Price
            price_frame = tk.Frame(self.root)
            price_frame.pack(pady=(0, 10))
            price_label = tk.Label(price_frame, text="Price:", font=("Arial", 16))
            price_label.pack(side=tk.LEFT)
            price_entry = tk.Label(price_frame, textvariable=self.price_var, font=("Arial", 16), pady=5)
            price_entry.pack(side=tk.RIGHT)

            # Charging Progress Bar
            charging_bar_frame = tk.Frame(self.root)
            charging_bar_frame.pack(pady=20)
            self.charging_bar = ttk.Progressbar(charging_bar_frame, orient="horizontal", length=200, mode="determinate")
            self.charging_bar.pack()

            # Buttons
            cancel_button = tk.Button(self.root, text="Cancel", command=self.do_nothing, font=("Arial", 16))
            cancel_button.pack(side=tk.LEFT, padx=20, pady=20)
            
            pay_button = tk.Button(self.root, text="Pay", command=self.pay, font=("Arial", 16))
            pay_button.pack(side=tk.RIGHT, padx=20, pady=20)

            # Start charging process in a separate thread
            threading.Thread(target=self.update_charging_progress).start()
            
            print("Charging screen loaded")  # Print to console when screen loaded
        except:
            messagebox.showinfo("noC", "No available chargers")
            self.stm.send('PB')
            #self.reset_and_goto_login()

    
    def update_charging_progress(self):
        """Logic that updates battery life, range and finally when the charging is done, the price """
        print("Updating started")
        # Subscribe to the MQTT topic where battery life and cost information is published
        topic = "ttm4115/team19/station/" + str(self.car_id) + "/"
        self.mqttClient.subscribe(topic)

        while True:
            # Get the last message received on the topic
            message = self.mqttClient.get_last_message(topic)

            # Check if the message is not empty
            if message is not None:
                try:
                    # Split the message to extract the value
                    parts = message.split("/")
                    value = float(parts[-1])  

                    if parts[-2] == "battery_life":
                        self.initial_battery = value
                        self.battery_level_var.set(str(value))
                        self.range_var.set(str(value * 2) + " km")  

                        # Update the progress bar based on battery level
                        self.charging_bar['value'] = value

                    elif parts[-2] == "cost":
                        self.price_var.set(str(int(value)) + "€")

                    else:
                        print("Unknown message type:", message)

                except ValueError as e:
                    # Handle non-numeric values
                    print("Error extracting value:", e)

            # Update the GUI to reflect the changes
            self.root.update()

            time.sleep(0.5)


    def do_nothing(self):
        """Handles communication with server when wanting to cancel, doesn't actually do_nothing """
        print("Cancel button pressed")

        start_action = {"type": "action", "status": "cancel", "token": self.token, "battery_level": 50}

        try:
            response = self.send_custom_post_request(start_action)
            response = response.json()
            print("Response is ", response)
            self.cancel = True
            messagebox.showinfo("Cancel", "Charging canceled")
        except:
            print("Wrong credentials")
        pass


    def reset_and_goto_login(self):
            """Resets login variables"""
            self.clear_screen()
            # Reset all variables

            self.root.title("ChargeUp!")
            self.root.geometry("300x500")  # Larger window size
            self.current_screen = None
            self.username = ""
            self.password = ""
            self.httpClient = BasicClient(self.ipAdress)
            self.mqttClient = MQTTClient()
            self.token = None  
            self.initial_cost = 0
            self.cancel = False
    
            
            # Clear the screen
            self.clear_screen()
            
            # Go back to the login screen
            self.login_screen()
     

    def pay(self):
        """Payment pop up, only works when charging is finished or canceled. So the price is displayed"""
        print("INFO IS " + str(self.cancel) + " " + str(self.initial_battery))
        if (self.cancel==True or self.initial_battery>99):
            messagebox.showinfo("Payment", "Thank you!")
            self.stm.send('PB')
            #self.reset_and_goto_login()
    

    def clear_screen(self):
        """Clears whole screen"""
        if self.current_screen:
            for widget in self.root.winfo_children():
                widget.destroy()


    def send_custom_post_request(self, data):
        """Handles logic to send post request to server"""
        # If we have a token, include it in every POST request
        if self.token:
            data['token'] = self.token

        # Convert dictionary to JSON string
        json_data = json.dumps(data)
        print(f"Sending a custom POST request with {json_data}")
        response = self.httpClient.send_post_request(data=json_data)

        # Print server response for POST request
        print("Response status from server:", response.status_code)
        print("Response text from server:", response.text)

        # Check if the response contains a token and save it
        if response.status_code == 200 and 'token' in response.json():
            self.token = response.json()['token']

        return response


if __name__ == "__main__":
    ip_adress = input("Local ip adress ") # User has to input their wifi adress
    initial_level = input("Please enter the initial battery level (%): ") # User has to input car initial battery life for simulation
    try:

        initial_level = int(initial_level)  # Convert the input to an integer

        app = ChargeUpApp(initial_level, ip_adress)  # Create an instance of the app with the initial battery level

        
    except ValueError:
        print("Invalid input! Please enter a numeric value.")



