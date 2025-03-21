import inspect
import json
import logging
import os
import sys
import traceback
from google.cloud import logging as cloud_logging
from google.oauth2 import service_account
from io import StringIO


def get_gcp_logger(log_name):
    gcp_credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    gcp_credentials_json = os.environ.get('GCP_CREDENTIALS_JSON')

    if not gcp_credentials_path and not gcp_credentials_json:
        raise ValueError(
            "Neither GOOGLE_APPLICATION_CREDENTIALS nor GCP_CREDENTIALS_JSON environment variable is set")

    try:
        if gcp_credentials_json:
            # Parse the JSON string into a dictionary
            credentials_dict = json.loads(gcp_credentials_json)

            # Create credentials object from the dictionary
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict)

            # Instantiate a client with explicit credentials
            client = cloud_logging.Client(credentials=credentials)
        else:
            # Use the default client
            client = cloud_logging.Client()

        # Create a custom logger
        _ = client.logger(log_name)

        # Create a Python logging handler that uses the Cloud Logging client
        handler = cloud_logging.handlers.CloudLoggingHandler(
            client, name=log_name)

        # Create a Python logger and add the Cloud Logging handler
        python_logger = logging.getLogger(log_name)
        python_logger.setLevel(logging.INFO)
        python_logger.addHandler(handler)

        return python_logger
    except json.JSONDecodeError:
        raise ValueError(
            "Invalid JSON in GCP_CREDENTIALS environment variable")
    except Exception as e:
        raise Exception(f"Error setting up GCP logging: {str(e)}")


class GCPExceptionHandler:
    def __init__(self, logger, original_stderr):
        self.logger = logger
        self.original_stderr = original_stderr

    def handle(self, exc_type, exc_value, exc_traceback):
        # Log to GCP
        tb = traceback.extract_tb(exc_traceback)
        filename, lineno, _, _ = tb[-1]

        message = f"Uncaught exception in {filename}, line {lineno}: {exc_type.__name__}: {exc_value}"

        record = logging.LogRecord(
            name=self.logger.name,
            level=logging.ERROR,
            pathname=filename,
            lineno=lineno,
            msg=message,
            args=None,
            exc_info=(exc_type, exc_value, exc_traceback),
        )

        self.logger.handle(record)

        # Log to original stderr
        traceback.print_exception(
            exc_type, exc_value, exc_traceback, file=self.original_stderr)


class GCPLogger:
    def __init__(self, logger):
        self.logger = logger
        self.buffer = StringIO()

    def write(self, message):
        self.buffer.write(message)
        if '\n' in message:
            self.flush()

    def flush(self):
        message = self.buffer.getvalue().strip()
        if message:
            caller = inspect.currentframe().f_back
            filename = caller.f_code.co_filename
            lineno = caller.f_lineno

            record = logging.LogRecord(
                name=self.logger.name,
                level=logging.INFO,
                pathname=filename,
                lineno=lineno,
                msg=message.strip(),
                args=None,
                exc_info=None
            )

            self.logger.handle(record)
        self.buffer.truncate(0)
        self.buffer.seek(0)

    def __getattr__(self, attr):
        return getattr(self.logger, attr)


def setup_gcp_logging(log_name):
    logger = get_gcp_logger(log_name)

    original_stderr = sys.stderr

    # Set up GCP logging for stdout
    sys.stdout = GCPLogger(logger)

    # Set up exception handling
    exception_handler = GCPExceptionHandler(logger, original_stderr)
    sys.excepthook = exception_handler.handle
