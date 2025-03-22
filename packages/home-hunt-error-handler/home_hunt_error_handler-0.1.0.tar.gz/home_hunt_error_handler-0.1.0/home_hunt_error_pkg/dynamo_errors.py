from botocore.exceptions import ClientError
from .exceptions import DatabaseError

class DynamoErrorHandler:
    """
    Class to handle DynamoDB specific errors and provide meaningful error messages or actions.
    """

    @staticmethod
    def handle_errors(exception):
        """
        Parse DynamoDB errors and return a user-friendly DatabaseError exception.

        :param exception: ClientError, the exception received from DynamoDB operations
        :return: DatabaseError, with a friendly message and error code
        """
        if isinstance(exception, ClientError):
            error_code = exception.response['Error']['Code']
            error_message = exception.response['Error']['Message']
            
            error_mapping = {
                'ResourceNotFoundException': "The requested resource was not found.",
                'ExpiredTokenException': "Your session token has expired. Please log in again.",
                'ValidationException': "The provided data does not meet validation requirements.",
                'ConditionalCheckFailedException': "Preconditions set for the operation did not hold true.",
                'ProvisionedThroughputExceededException': "You have exceeded your provisioned throughput limits.",
                'InternalFailure': "An internal error occurred within DynamoDB.",
                'ThrottlingException': "Request throttled due to excessive requests."
            }

            mapped_message = error_mapping.get(error_code, f"An unexpected DynamoDB error occurred: {error_message}")
            return DatabaseError(mapped_message, error_code)
        else:
            # General exception for non-client errors
            return DatabaseError(f"An unexpected error occurred: {str(exception)}")

    @staticmethod
    def is_retryable(exception):
        """
        Determine if the error is retryable based on the error code.

        :param exception: ClientError, the exception received from DynamoDB operations
        :return: bool, True if the error suggests that the operation can be retried
        """
        if isinstance(exception, ClientError):
            # List of retryable DynamoDB error codes
            retryable_errors = [
                'ProvisionedThroughputExceededException',
                'ThrottlingException',
                'LimitExceededException',
                'InternalFailure'
            ]
            error_code = exception.response['Error']['Code']
            return error_code in retryable_errors
        return False
