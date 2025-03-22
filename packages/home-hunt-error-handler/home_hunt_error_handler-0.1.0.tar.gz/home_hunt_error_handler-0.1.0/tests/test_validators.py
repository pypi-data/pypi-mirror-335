import unittest
from home_hunt_error_pkg.validators import Validator
from home_hunt_error_pkg.exceptions import ValidationError

class TestValidator(unittest.TestCase):

    def test_validate_required_fields(self):
        data = {
            'email': '',
            'password': 'TestPass123!'
        }
        fields = ['email', 'password', 'username']

        with self.assertRaises(ValidationError) as context:
            Validator.validate_required_fields(data, fields)

        self.assertIn('username', str(context.exception))

    def test_validate_phone_number_valid(self):
        """Test validate_phone_number with a valid Irish phone number."""
        phone = '+353851234567'
        # Should not raise an exception
        Validator.validate_phone_number(phone)

    def test_validate_phone_number_invalid(self):
        """Test validate_phone_number with an invalid phone number."""
        phone = '0851234567'  # Missing international prefix +353
        with self.assertRaises(ValidationError) as context:
            Validator.validate_phone_number(phone)

        self.assertIn('Phone must be in Irish format', str(context.exception))

    def test_validate_passwords_matching(self):
        """Test validate_passwords with matching passwords."""
        password1 = 'ValidPass123!'
        password2 = 'ValidPass123!'
        # Should not raise an exception
        Validator.validate_passwords(password1, password2)

    def test_validate_passwords_non_matching(self):
        """Test validate_passwords with non-matching passwords."""
        password1 = 'ValidPass123!'
        password2 = 'InvalidPass123!'
        with self.assertRaises(ValidationError) as context:
            Validator.validate_passwords(password1, password2)

        self.assertIn('Passwords do not match', str(context.exception))

    def test_validate_passwords_weak_password(self):
        """Test validate_passwords with a weak password."""
        password1 = 'weak'
        password2 = 'weak'
        with self.assertRaises(ValidationError) as context:
            Validator.validate_passwords(password1, password2)

        self.assertIn('Password must be at least 8 characters', str(context.exception))

    def test_validate_email_valid(self):
        """Test validate_email with a valid email address."""
        email = 'user@example.com'
        # Should not raise an exception
        Validator.validate_email(email)

    def test_validate_email_invalid(self):
        """Test validate_email with an invalid email address."""
        email = 'user@com'
        with self.assertRaises(ValidationError) as context:
            Validator.validate_email(email)

        self.assertIn('Invalid email address format', str(context.exception))

if __name__ == '__main__':
    unittest.main()
