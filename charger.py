import time
import pygame
import stmpy

print("STMPY Version installed: {}".format(stmpy.__version__))

class Charger:
    
    def __init__(self, charger_id):
        """Simulates charger, has id as input and it's global parameters are defined below"""
        self.charger_id = charger_id
        self.is_charging = False
        self.allowed_car_id = None
        self.is_occupied = False
        self.price_per_minute = 100  # Euro per minute
        self.charging_start_time = None
        self.charging_cost = 0
        self.should_continue_charging = True  # Control flag

        pygame.mixer.init()  # Initialize the mixer module
        self.charging_sound = pygame.mixer.Sound('charging_sound.mp3')  # Load sound file


    def can_charge(self, car_id):
        """Checks if car is allowed to charge here"""
        return self.allowed_car_id == car_id
    

    def start_charging(self, car):
        """Starts charging, takes into account timestamp"""
        if self.can_charge(car.id):
            self.is_charging = True
            self.is_occupied = True
            self.charging_start_time = time.time()
            print(f"{self.charger_id} is now in use by car ID {car.id}.")
            self.should_continue_charging = True
            self.charge(car)


    def charge(self, car):
        """ Charging logic, sleep simulates charging"""
        car.is_charging = True
        self.is_charging = True
        self.is_occupied = True
        self.charging_start_time = time.time()

        self.charging_sound.play(-1) # Play charging sound

        # Stops if >100
        while car.battery_level < 100 and self.should_continue_charging:
            time.sleep(1)
            car.battery_level += 1
            car.send_message("ttm4115/team19/station/" + str(car.id) + "/" + "battery_life" + "/" + str(car.battery_level))
            print(f"Battery level updated to {car.battery_level}%")

        if car.battery_level >= 100:
            print(f"{self.charger_id} finished charging car ID {car.id}.")
        else:
            print(f"{self.charger_id} charging interrupted for car ID {car.id}.")

        self.charging_sound.stop() # Stop the sound when charging stops
        
        self.stop_charging(car)


    def stop_charging(self, car):
        """Stops the charging process and returns variables to initial value"""
        if not self.is_charging:
            return

        self.should_continue_charging = False # Signal to stop charging
        time.sleep(2)  # Allow some time for the loop to terminate

        # Check if charging start time is None
        if self.charging_start_time is None:
            print("Charging was not started properly.")
            return

        # Calculate charging duration and cost
        self.is_charging = False
        self.is_occupied = False
        charging_duration_minutes = (time.time() - self.charging_start_time) / 60
        self.charging_cost = charging_duration_minutes * self.price_per_minute # Cost depends on time
        print(f"{self.charger_id} is now available. Total cost: €{self.charging_cost:.2f}")
        car.send_message("ttm4115/team19/station/" + str(car.id) + "/" + "cost" + "/" + str(self.charging_cost))

        # Reset car and charger attributes
        car.is_charging = False
        self.allowed_car_id = None
        self.charging_start_time = None
        self.charging_cost = 0

