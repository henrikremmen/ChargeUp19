from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from station import Station
from car import Car
import time
import threading
from client import MQTTClient
import json
import secrets

users = {"tarik": ["tarikpass", "ABC123"], "henny":["hennypass", "BBB123"],
         "magnus":["magnuspass", "ZZZ123"], "mie":["miepass", "Z123"] }  # Example user database

tokens = {} # This will map tokens to usernamesç

cars = {} # Saves cars in system

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """This class allows each request to be handled in a new thread."""

class Server(BaseHTTPRequestHandler):
    """Server class, with all the necessary methods to handle requests"""

    station = Station(5050) 
    mqtt_client = MQTTClient()


    def handle(self):
        """Print a message each time a client connects, before handling the request"""
        print(f"Connection from: {self.client_address[0]}:{self.client_address[1]}")
        super().handle()


    def do_GET(self):   # Might not use
        """Responds to a GET request"""
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world! This is a GET request.')


    def handle_sign_in(self, data):
        """Handle sign in by user"""

        # Ger user's info
        username = data.get('username')
        password = data.get('password')
        
        if username in users and password in users[username]:
            # Generate user
            token = secrets.token_urlsafe(16)
            tokens[token] = username  # Store the token and associate it with the username
            
            # Send response
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = json.dumps({"message": "Sign in successful", "token": token})
            self.wfile.write(response.encode())
        else:
            # Error
            self.send_response(401)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Unauthorized: Incorrect username or password")


    def handle_action(self, data):
        """Handles cancel or start charging requests by user"""

        # Get token
        token = data.get('token')

        # Handle request
        if token and token in tokens:
            username = tokens[token]
            car_id = users[username][1]
            status = data.get('status')
            
            # User wants to start charging
            if status == "start":
                battery_life = data.get('battery_level')
                current_car = Car(id=car_id, battery_level=battery_life)  # Create the car instance
                cars[car_id] = current_car
                car = cars[car_id]
                users[username].append(car)
                charger_object = self.station.assign_charger(car)  # Assign a charger

                # Error case
                if charger_object is None:
                    self.send_response(503)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    response = json.dumps({"message": "No available chargers."})
                    self.wfile.write(response.encode())
                    return

                # Send initial info about the assignment to the phone
                station_id = self.station.station_id 
                charger_id = charger_object.charger_id
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = json.dumps({
                    "message": "Charger assigned",
                    "info": {
                        "station_id": station_id,
                        "charger_id": charger_id,
                        "car_id": car_id
                    }
                })

                # Send response
                self.wfile.write(response.encode())

                threading.Thread(target=self.start_process, args=(car,)).start()

            elif status == "cancel":
                # Handle cancel logic

                # Get charger object
                charger_object = self.station.find_charger_by_car_id(car_id)

                car_id = users[username][1]
                car = cars[car_id]

                print("BATTERY BEFORE CANCEL")
                print(car)
                
                # Stop charging
                if charger_object:
                    charger_object.stop_charging(car)
                    print("Charging has been canceled")
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    response = json.dumps({"message": "Action 'cancel' processed"})
                    self.wfile.write(response.encode())
                else:
                    self.send_error(400, "Bad Request: Unknown action")
        else:
            self.send_response(403)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Forbidden: Sign in required")


    def do_POST(self):
        """Recieves post requests and calls handle functions"""

        content_length = int(self.headers['Content-Length'])  # Get the size of data
        post_data = self.rfile.read(content_length)  # Get the data itself
        print("IN POST FUNCTION")
        print(post_data.decode('utf-8'))
        try:
            # Convert JSON string into a Python dictionary
            data = json.loads(post_data.decode('utf-8'))

            # Check the type of request and handle accordingly
            if data['type'] == 'sign_in':
                self.handle_sign_in(data)
            elif data['type'] == 'action':
                self.handle_action(data)
            else:
                self.send_error(400, "Bad Request: Unknown type")
        # Errors
        except json.JSONDecodeError:
            self.send_error(400, "Bad Request: Invalid JSON")
        except KeyError:
            self.send_error(400, "Bad Request: Missing necessary fields")
        except:
            print("Client connection failure")
        

    def find_charger_by_car_id(self, car_id):
        """Return charger by car_id"""
        for charger_id, charger in self.station.chargers.items():
            if charger.allowed_car_id == car_id:
                return charger
        return None


    def start_process(self, car):
        """Gets a charger for the user and initialize charging. Not actually an example need to change name"""

        print("Before charging:")

        charger_object = self.find_charger_by_car_id(car.id)

        if charger_object is None:
            print(f"No charger object found for ID {charger_object.charger_id}")
            return
        
        # Info before charging
        charger_id = charger_object.charger_id
        #self.station.check_charger_status()
        print(car)

        if charger_object.can_charge(car.id):
            charger_object.start_charging(car)  # This method now handles the entire charging process

        else:
            print(f"Charger {charger_id} cannot start charging or is already occupied.")

        # Display final statuses
        print("After charging:")
        print(car)

        print("Simulation complete.")


ip_adress = input("Local ip adress ") # User needs to input their own ip adress

server_address = (ip_adress, 8000)
httpd = ThreadedHTTPServer(server_address, Server)
print("Server started on " + str(server_address[0]))
httpd.serve_forever()

