from models import Fleet, EconomyVehicle, PremiumVehicle, ElectricVehicle
from helpers import MetroGoException

def main_menu():
    print("\n--- MetroGo Corporate Fleet Management Interface ---")
    print("1. Register a New Fleet Vehicle")
    print("2. List All Active Fleet Vehicles")
    print("3. Execute Polymorphic Dispatch Request")
    print("4. Exit")

def run():
    fleet = Fleet()
    
    try:
        fleet.register_vehicle(EconomyVehicle("11111111111111111", "Toyota Camry", 2.50, (6.52, 3.37)))
        fleet.register_vehicle(PremiumVehicle("22222222222222222", "Mercedes S-Class", 5.00, (6.55, 3.39)))
        fleet.register_vehicle(ElectricVehicle("33333333333333333", "Tesla Model Y", 3.00, (6.50, 3.35), 85))
    except MetroGoException as e:
        print(f"Initialization seeding error: {e}")

    while True:
        main_menu()
        choice = input("Enter option [1-4]: ").strip()
        try:
            if choice == "1":
                print("\n--- Register New Vehicle ---")
                v_type = input("Enter vehicle type (economy / premium / electric): ").strip().lower()
                vin = input("Enter 17-character alphanumeric VIN: ").strip()
                model = input("Enter model name: ").strip()
                base_rate = float(input("Enter base rate (e.g., 2.50): ").strip())
                lat = float(input("Enter pickup Latitude (-90 to 90): ").strip())
                lon = float(input("Enter pickup Longitude (-180 to 180): ").strip())
                location = (lat, lon)

                if v_type == "economy":
                    vehicle = EconomyVehicle(vin, model, base_rate, location)
                elif v_type == "premium":
                    vehicle = PremiumVehicle(vin, model, base_rate, location)
                elif v_type == "electric":
                    battery = int(input("Enter battery level (0-100): ").strip())
                    vehicle = ElectricVehicle(vin, model, base_rate, location, battery)
                else:
                    print("Unknown vehicle type specified. Registration aborted.")
                    continue

                fleet.register_vehicle(vehicle)
                print(f"\n[SUCCESS] Vehicle {vin} ({model}) successfully registered!")

            elif choice == "2":
                print("\n--- Active Fleet Vehicles ---")
                vehicles = fleet.get_all_vehicles()
                if not vehicles:
                    print("No vehicles currently registered in the fleet.")
                else:
                    print(f"{'VIN':<20} | {'Model':<20} | {'Type':<18} | {'Base Rate':<10} | {'Location':<15}")
                    print("-" * 88)
                    for v in vehicles:
                        v_class_name = v.__class__.__name__
                        print(f"{v.vin:<20} | {v.model_name:<20} | {v_class_name:<18} | ${v.base_rate:<9.2f} | {str(v.current_location):<15}")

            elif choice == "3":
                print("\n--- Execute Polymorphic Dispatch Request ---")
                lat = float(input("Enter passenger Latitude (-90 to 90): ").strip())
                lon = float(input("Enter passenger Longitude (-180 to 180): ").strip())
                distance = float(input("Enter trip distance in miles: ").strip())
                surge = float(input("Enter surge multiplier (e.g., 1.0 for normal): ").strip())
                
                requires_prem = input("Requires premium vehicle? (y/n): ").strip().lower() == 'y'
                min_bat_input = input("Minimum battery requirement for EVs (press Enter for default 20%): ").strip()
                
                trip_reqs = {
                    "pickup_location": (lat, lon),
                    "requires_premium": requires_prem,
                    "min_battery": int(min_bat_input) if min_bat_input else 20
                }

                candidates = fleet.query_dispatchable_fleet(trip_reqs)
                best_vehicle = candidates[0] 

                fare = best_vehicle.calculate_fare(distance, surge)
                print(f"\n[DISPATCH SUCCESS] Assigned Vehicle:")
                print(f" - Model: {best_vehicle.model_name} ({best_vehicle.__class__.__name__})")
                print(f" - VIN: {best_vehicle.vin}")
                print(f" - Location: {best_vehicle.current_location}")
                print(f" - Calculated Trip Fare: ${fare:.2f}")

            elif choice == "4":
                print("Exiting MetroGo. System Offline.")
                break
            else:
                print("Invalid option selected. Please select a valid choice.")

        except MetroGoException as e:
            print(f"\n[EXECUTION ERROR] MetroGo caught validation failure: {e}")
        except ValueError:
            print("\n[INPUT ERROR] Please enter valid numeric formats for rates, coordinates, or distances.")
        except Exception as e:
            print(f"\n[CRITICAL ERROR] Unexpected failure in runtime stack: {e}")

if __name__ == "__main__":
    run()