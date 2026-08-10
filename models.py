from abc import ABC, abstractmethod
import math
from helpers import (
    VehicleValidationError,
    InvalidLocationError,
    DispatchFailureException
)

IBADAN_LOCATIONS = {
    "bodija": (7.4211, 3.9015),
    "dugbe": (7.3916, 3.8824),
    "challenge": (7.3565, 3.8741),
    "ring road": (7.3776, 3.8647),
    "akobo": (7.4474, 3.9351),
    "basorun": (7.4201, 3.9213),
    "sango": (7.4278, 3.8965),
    "ui": (7.4422, 3.8998),
    "samonda": (7.4292, 3.8941),
    "mokola": (7.4111, 3.8912),
    "apata": (7.3321, 3.8342),
    "oluyole": (7.3621, 3.8512),
    "eleiyele": (7.4085, 3.8612),
    "agodi gate": (7.4089, 3.9078),
    "ojoo": (7.4785, 3.9125),
    "iwo road": (7.4125, 3.9342),
    "bodija market": (7.4305, 3.9056),
    "bodija estate": (7.4255, 3.9088),
    "bashorun": (7.4201, 3.9213),
    "bodija extension": (7.4188, 3.9102)
}

def resolve_location(loc_input) -> tuple:
    """Resolves a string area name or a raw coordinate tuple into standard coordinates."""
    if isinstance(loc_input, tuple):
        return loc_input
    if isinstance(loc_input, str):
        cleaned = loc_input.strip().lower()
        if cleaned in IBADAN_LOCATIONS:
            return IBADAN_LOCATIONS[cleaned]
        elif "," in cleaned:
            try:
                parts = cleaned.split(",")
                return (float(parts[0].strip()), float(parts[1].strip()))
            except ValueError:
                pass
    raise InvalidLocationError(
        f"Unknown location '{loc_input}'. Please choose from known areas like "
        "Bodija, Dugbe, Challenge, Ring Road, Akobo, Basorun, Sango, UI, Samonda, Mokola, Apata, Oluyole, Eleiyele, Agodi Gate, Ojoo, Iwo Road.")

def get_location_name(coords: tuple) -> str:
    """Takes a coordinate tuple and returns the corresponding Ibadan area name if found."""
    for name, lat_lon in IBADAN_LOCATIONS.items():
        # Check coordinates with a tiny tolerance for floating-point safety
        if abs(lat_lon[0] - coords[0]) < 0.0001 and abs(lat_lon[1] - coords[1]) < 0.0001:
            return name.title() # Capitalizes the first letter (e.g., "Bodija")
    return f"{coords}" # Fallback to showing coordinates if it doesn't match a preset

class Vehicle(ABC):

    def __init__(self, vin: str, model_name: str, base_rate: float, location: tuple):
        self.vin = vin 
        self.model_name = model_name
        self.base_rate = base_rate
        self.current_location = location

    @property
    def vin(self) -> str:
        return self._vin

    @vin.setter
    def vin(self, value: str):
        if not isinstance(value, str) or len(value) != 17 or not value.isalnum():
            raise VehicleValidationError(f"Invalid VIN: '{value}'. VIN must be exactly 17 alphanumeric characters.")
        self._vin = value.upper()

    @property
    def model_name(self) -> str:
        return self._model_name

    @model_name.setter
    def model_name(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise VehicleValidationError("Model name must be a non-empty string.")
        self._model_name = value

    @property
    def base_rate(self) -> float:
        return self._base_rate

    @base_rate.setter
    def base_rate(self, value: float):
        if not isinstance(value, (int, float)) or value <= 0.0:
            raise VehicleValidationError("Base rate must be strictly positive (greater than 0.0).")
        self._base_rate = float(value)

    @property
    def current_location(self) -> tuple:
        return self._current_location

    @current_location.setter
    def current_location(self, value):
        # Resolve string area names to coordinates automatically
        resolved_value = resolve_location(value)
        
        if not isinstance(resolved_value, tuple) or len(resolved_value) != 2:
            raise InvalidLocationError("Location must be a tuple containing (latitude, longitude).")
        lat, lon = resolved_value
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            raise InvalidLocationError("Latitude and longitude must be numeric values.")
        if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
            raise InvalidLocationError(f"Latitude ({lat}) or Longitude ({lon}) out of bounds.")
        self._current_location = resolved_value


    @abstractmethod
    def calculate_fare(self, distance_miles: float, surge_multiplier: float) -> float:
        """Calculate trip fare based on concrete vehicle tier behavior."""
        pass

    @abstractmethod
    def verify_dispatch_viability(self, trip_requirements: dict) -> bool:
        """Verify if the vehicle can fulfill specific trip criteria polymorphically."""
        pass


class EconomyVehicle(Vehicle):

    def calculate_fare(self, distance: float, surge: float) -> float:
        return round(distance * self.base_rate * surge, 2)

    def verify_dispatch_viability(self, trip_requirements: dict) -> bool:
        return True


class PremiumVehicle(Vehicle):
    LUXURY_COEFFICIENT = 1.5
    BOOKING_FEE = 15.00

    def calculate_fare(self, distance: float, surge: float) -> float:
        base_calculation = distance * self.base_rate * surge * self.LUXURY_COEFFICIENT
        return round(base_calculation + self.BOOKING_FEE, 2)

    def verify_dispatch_viability(self, trip_requirements: dict) -> bool:
        return trip_requirements.get("requires_premium", False)


class ElectricVehicle(Vehicle):

    def __init__(self, vin: str, model_name: str, base_rate: float, location: tuple, battery_level: int = 100):
        super().__init__(vin, model_name, base_rate, location)
        self.battery_level = battery_level

    @property
    def battery_level(self) -> int:
        return self._battery_level

    @battery_level.setter
    def battery_level(self, value: int):
        if not isinstance(value, int) or not (0 <= value <= 100):
            raise VehicleValidationError("Battery level must be an integer between 0 and 100.")
        self._battery_level = value

    def calculate_fare(self, distance: float, surge: float) -> float:
        return round(distance * self.base_rate * surge * 0.9, 2)

    def verify_dispatch_viability(self, trip_requirements: dict) -> bool:
        min_charge = trip_requirements.get("min_battery", 20)
        return self.battery_level >= min_charge


class Fleet:

    def __init__(self):
        self._vehicles = {} 

    def register_vehicle(self, vehicle: Vehicle) -> None:
        if vehicle.vin in self._vehicles:
            raise VehicleValidationError(f"Vehicle with VIN {vehicle.vin} is already registered.")
        self._vehicles[vehicle.vin] = vehicle

    def remove_vehicle(self, vin: str) -> None:
        upper_vin = vin.upper()
        if upper_vin not in self._vehicles:
            raise VehicleValidationError(f"Vehicle with VIN {upper_vin} does not exist in the fleet.")
        del self._vehicles[upper_vin]

    def get_all_vehicles(self) -> list[Vehicle]:
        return list(self._vehicles.values())

    def query_dispatchable_fleet(self, trip_requirements: dict) -> list[Vehicle]:
        eligible_vehicles = []
        pickup_loc = trip_requirements.get("pickup_location")

        for vehicle in self._vehicles.values():
            if vehicle.verify_dispatch_viability(trip_requirements):
                if pickup_loc:
                    lat1, lon1 = pickup_loc
                    lat2, lon2 = vehicle.current_location
                    distance = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
                    eligible_vehicles.append((distance, vehicle))
                else:
                    eligible_vehicles.append((0.0, vehicle))

        if not eligible_vehicles:
            raise DispatchFailureException("No viable vehicles available matching the requested trip criteria.")

        # Sort by proximity (distance) ascending
        eligible_vehicles.sort(key=lambda x: x[0])
        return [v[1] for v in eligible_vehicles]