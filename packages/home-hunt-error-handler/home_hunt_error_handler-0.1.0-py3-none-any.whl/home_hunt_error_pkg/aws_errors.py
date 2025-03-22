from .exceptions import ValidationError, DatabaseError
from botocore.exceptions import ClientError

class AWSErrorHandler:
    """
    Class to handle errors from AWS services such as Cognito and DynamoDB.
    """

    @staticmethod
    def handle_cognito_errors(exception):
        """
        Handle AWS Cognito specific errors and map them to a more user-friendly format.
        
        :param exception: ClientError, the caught exception from AWS Cognito operations
        :return: ValidationError with appropriate message and field based on the error code
        """
        error_code = exception.response['Error']['Code']
        error_message = exception.response['Error']['Message']
        
        error_mapping = {
            'UsernameExistsException': ('username', 'Username already exists'),
            'InvalidPasswordException': ('password1', 'Password must be at least 8 characters long and include at least one number, one special character, one uppercase letter, and one lowercase letter'),
            'InvalidParameterException': ('email', 'Invalid email address'),
            'CodeDeliveryFailureException': ('email', 'Failed to send verification code'),
            'InvalidPhoneNumberException': ('phone', 'Invalid phone number format'),
            'CodeMismatchException': ('code', 'Invalid verification code'),
            'ExpiredCodeException': ('code', 'Verification code has expired, please request a new one'),
            'UserNotFoundException': ('general', 'User does not exist'),
            'NotAuthorizedException': ('general', 'Invalid username or password')
        }

        field, message = error_mapping.get(error_code, ('general', f"An unexpected error occurred: {error_message}"))
        return ValidationError(message, field)

    @staticmethod
    def handle_dynamo_errors(exception):
        """
        Handle AWS DynamoDB specific errors and map them to a more user-friendly or actionable format.
        
        :param exception: ClientError, the caught exception from AWS DynamoDB operations
        :return: DatabaseError with appropriate message based on the error code
        """
        if isinstance(exception, ClientError):
            error_code = exception.response['Error']['Code']
            error_message = exception.response['Error']['Message']
            
            error_mapping = {
                'ResourceNotFoundException': "Requested resource not found.",
                'ExpiredTokenException': "Security token included in the request is expired.",
                'ValidationException': "The inputs to the request are invalid.",
                'ConditionalCheckFailedException': "Condition check specified in the operation failed.",
                'ProvisionedThroughputExceededException': "Requested throughput exceeded the current capacity of your table.",
                'InternalFailure': "Internal error occurred, please try again."
            }

            mapped_message = error_mapping.get(error_code, f"An unexpected DynamoDB error occurred: {error_message}")
            return DatabaseError(mapped_message, error_code)
        else:
            return DatabaseError("An unexpected error occurred.", None)

