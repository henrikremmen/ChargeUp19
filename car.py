from client import MQTTClient
import stmpy
from stmpy import Machine, Driver

class Car(MQTTClient):

    def __init__(self, id, battery_level=0):
        """Defines a car, with input as car_ d and battery level"""
        super().__init__()
        self.id = id
        self.battery_level = battery_level
        self.is_charging = False

        self.topic = "ttm4115/team19/station/" + str(self.id) + "/"  # Topic to send requests to
        self.connected = False
        self.connect_and_subscribe() 


    def connect_and_subscribe(self):
        """Connects and subscribes to the server and topic, using methodsin MQTTClient class"""
        if not self.connected:
            self.connect()  # Connect to the MQTT broker if not already connected
            self.subscribe(self.topic)  # Subscribe to the replies topic
            self.connected = True
            print(f"Car is connected and subscribed to {self.topic}")
            self.client.loop_start()  # Start the loop to keep the connection
        else:
            print("Car is already connected to the MQTT broker.")


    def __str__(self):
        """Returns the current status of the car"""
        return f"Car(id={self.id}, battery_level={self.battery_level}, is_charging={self.is_charging})"


    def send_message(self, message):
        """Publish a message to the request topic"""
        self.publish(self.topic, message)
        print(f"Message sent to '{self.topic}': '{message}'")
    

    def disconnect_from_server(self):
        """Disconnects from server"""
        if self.connected:
            self.client.loop_stop()  # Stop the loop before disconnecting
            self.disconnect()  # Disconnect from the MQTT broker
            self.connected = False
            print("Phone has disconnected from the server.")
        else:
            print("Phone is already disconnected from the server.")


    def current_light(self):
        """For the theoretical state machine, but not actually in use"""
        if self.battery_level <= 30:
            print("Battery is low")
        elif self.battery_level <= 70:
            print("Battery is medium")
        else:
            print("Battery if full")        


# State machine implementation but didnt manage to fix it in the sytem
# It supposed to categorize the cars batttery level in "low, medium, high"
# And change the lights depending on where it is

"""
newCar = Car("CCC123")
newCar.batter_level = 90

# State machine
t0 = {"source": "initial", 
    "target": "start"}

t1 = {"trigger": "s1", 
    "source": "start",
    "target": "low",
    "effect": "current_light"}

t2 = {"trigger": "s2", 
    "source": "start",
    "target": "medium",
    "effect": "current_light"}

t3 = {"trigger": "s3", 
    "source": "start",
    "target": "high",
    "effect": "current_light"}

t4 = {"trigger": "s2", 
    "source": "low",
    "target": "medium",
    "effect": "current_light"}

t5 = {"trigger": "s3", 
    "source": "medium",
    "target": "high",
    "effect": "current_light"}

t6 = {"trigger": "s2", 
    "source": "high",
    "target": "medium",
    "effect": "current_light"}

t7 = {"trigger": "s1", 
    "source": "medium",
    "target": "low",
    "effect": "current_light"}

machine = Machine(name='car', transitions=[t0, t1, t2, t3, t4, t5, t6, t7], obj=Car)
newCar.stm = machine

driver = Driver()
driver.add_machine(machine)

driver.start()"""









