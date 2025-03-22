import re
from .exceptions import ValidationError

class Validator:
    """
    A class to handle various validations for input data.
    """

    @staticmethod
    def validate_required_fields(data, fields):
        """
        Ensure that all specified fields are present and not empty in the given data.
        
        :param data: dict, the data to check
        :param fields: list, the fields that must be present and not empty
        :raises ValidationError: If any of the specified fields are missing or empty
        """
        missing = [field for field in fields if not data.get(field)]
        if missing:
            raise ValidationError("All fields are required.", ','.join(missing))

    @staticmethod
    def validate_phone_number(phone):
        """
        Validate an Irish phone number format.

        :param phone: str, the phone number to validate
        :raises ValidationError: If the phone number is not in the correct format
        """
        if not re.match(r'^\+353\d{9}$', phone):
            raise ValidationError("Phone must be in Irish format (+353 followed by 9 digits, e.g., +353851234567)", 'phone')

    @staticmethod
    def validate_passwords(password1, password2):
        """
        Validate that passwords are the same and meet a minimum security standard.
        
        :param password1: str, the first password to validate
        :param password2: str, the second password to validate
        :raises ValidationError: If the passwords do not match or do not meet security standards
        """
        if password1 != password2:
            raise ValidationError("Passwords do not match.", 'password2')
        if len(password1) < 8 or not re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W)', password1):
            raise ValidationError("Password must be at least 8 characters long and include at least one number, one special character, one uppercase letter, and one lowercase letter.", 'password1')

    @staticmethod
    def validate_email(email):
        """
        Validate that an email address is in a proper format.
        
        :param email: str, the email to validate
        :raises ValidationError: If the email format is invalid
        """
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValidationError("Invalid email address format.", 'email')

