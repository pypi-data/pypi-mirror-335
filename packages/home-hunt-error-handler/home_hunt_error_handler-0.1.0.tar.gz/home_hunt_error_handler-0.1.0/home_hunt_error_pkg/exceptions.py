class ValidationError(Exception):
    """
    Exception raised for errors in the input validation.
    Attributes:
        message -- explanation of the error
        field -- the field on which the validation error occurred
    """
    def __init__(self, message, field):
        self.message = message
        self.field = field
        super().__init__(f"{field}: {message}")

class DatabaseError(Exception):
    """
    Exception raised for errors that are related to database operations.
    Attributes:
        message -- explanation of the error
        code -- optional error code from the database if applicable
    """
    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(f"Error {code}: {message}" if code else message)
