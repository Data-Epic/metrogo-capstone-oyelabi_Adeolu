# Custom Domain Exceptions and Validation Constants

class MetroGoException(Exception):
    """Base exception class for all MetroGo runtime errors."""
    pass

class VehicleValidationError(MetroGoException):
    """Raised when parameter bounds check on properties fails."""
    pass

class InvalidLocationError(MetroGoException):
    """Raised when spatial coordinate pairs contain faulty definitions."""
    pass

class DispatchFailureException(MetroGoException):
    """Raised when routing algorithms cannot discover matching assets."""
    pass