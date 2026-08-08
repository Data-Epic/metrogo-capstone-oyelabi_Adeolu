# MetroGo Dynamic Fleet Dispatch System

---

## Project Overview
The MetroGo Dynamic Fleet Dispatch System is an enterprise-grade urban ride-hailing simulation engine developed as the final Object-Oriented Programming (OOP) capstone for the DataEpic technical series. The system is designed to handle multi-modal transportation requests efficiently, focusing on robust encapsulation, inheritance, composition, and polymorphism.

---

## Features
- **OOP Architecture**: Built using a strict, modular three-file structure which are:
   - helpers.py
   - models.py
   - dispatch_app.py
- **Dynamic Dispatch**: Implements polymorphic dispatching, avoiding brittle conditional type-checking (`isinstance` or `type`).
- **Data Integrity**: Uses strict property validation for all vehicle attributes (VIN, coordinates, battery levels).
- **Custom Error Handling**: Implements a dedicated domain-specific exception hierarchy for graceful failure management.
- **Interactive CLI**: A robust command-line interface for fleet management and simulation.

---

## System Architecture
The project is modularized into three core components:

| Module | Responsibility |
| :--- | :--- |
| `helpers.py` | Contains custom domain exceptions, constants, and logging setups. |
| `models.py` | Defines the `Vehicle` base class, subclasses (Economy, Premium, Electric), and the `Fleet` composition manager. |
| `dispatch_app.py` | The executable entry point providing the interactive CLI. |

---

## Major Python Concept Used

* **Encapsulation & Validation**: Protect attributes (like `vin` or `current_location`) using private variables (e.g., `self._vin`) and `@property` setters with validation. When someone inputs a bad VIN or out-of-bound GPS coordinates, it raises custom exceptions.


* **Inheritance & `super()**`: Create a base `Vehicle` class, then inherit from it for `EconomyVehicle`, `PremiumVehicle`, and `ElectricVehicle`. Used `super().__init__(...)` to reuse the parent's initialization logic.


* **Composition**: Create a `Fleet` class that holds a collection (list) of vehicle objects. It should have methods to `register_vehicle()`, `remove_vehicle()`, and `query_dispatchable_fleet()`.


* **Polymorphism (CRITICAL!)**:
* Never use `isinstance()` or `type()` to check what kind of car you are dealing with inside  dispatch logic.


* Instead, give every vehicle class its own version of `calculate_fare()` and `verify_dispatch_viability()`. Python will automatically figure out which method to run based on the object type.

---

## Installation & Setup
1. **Clone the Repository**:
   ```bash
   git clone <-repo-url>
   cd metrogo-capstone-<username>