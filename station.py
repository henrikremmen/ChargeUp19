import time
from charger import Charger
from car import Car

class Station:
    
    def __init__(self, id):
        """Station object, with several chargers"""

        self.station_id = id
        self.coordinates = 0 # Will use later maybe
        self.chargers = {f"Charger_{i}": Charger(f"Charger_{i}") for i in range(1,4)} # Initialize chargers with unique IDs. There are 3


    def check_charger_status(self):
        """Check the status of all chargers"""
        for charger_id, charger in self.chargers.items():
            status = "In use" if charger.is_charging else "Available"
            allowed_status = f"Allowed for car ID {charger.allowed_car_id}" if charger.allowed_car_id else "Not allowed"
            print(f"{charger_id}: {status}, {allowed_status}")


    def authorize_charger(self, charger_id, car_id):
        """Authorize charger for a specific car"""
        if charger_id in self.chargers:
            self.chargers[charger_id].authorize_car_charging(car_id)
        else:
            print(f"{charger_id} does not exist.")


    def start_charging_on_charger(self, charger_id, car):
        """Start charging on a specific charger"""
        if charger_id in self.chargers:
            if not self.chargers[charger_id].is_occupied:
                self.chargers[charger_id].start_charging(car)
                print(f"Started charging on {charger_id}.")
            else:
                print(f"{charger_id} is already in use.")
        else:
            print(f"{charger_id} does not exist.")


    def stop_charging_on_charger(self, charger_id, car):
        """Stop charging on a specific charger"""
        if charger_id in self.chargers:
            if self.chargers[charger_id].is_occupied:
                self.chargers[charger_id].stop_charging(car)
                print(f"Stopped charging on {charger_id}.")
            else:
                print(f"{charger_id} is not currently in use.")
        else:
            print(f"{charger_id} does not exist.")
    

    def assign_charger(self, car):
        """Assignes charger to a car"""
        for charger_id, charger in self.chargers.items():
            if not charger.is_occupied:
                charger.is_occupied = True
                charger.allowed_car_id = car.id
                return charger
        print(f"No charger was found")
        return None
    

    def find_charger_by_car_id(self, car_id):
        """Returns charger by car id"""
        for charger_id, charger in self.chargers.items():
            if charger.allowed_car_id == car_id:
                return charger
        return None


