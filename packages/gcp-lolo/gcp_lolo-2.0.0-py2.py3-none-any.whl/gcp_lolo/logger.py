import inspect
import json
import logging
import os
import sys
import traceback
from google.cloud import logging as cloud_logging
from google.oauth2 import service_account
from google.cloud.logging_v2.handlers import CloudLoggingHandler
from google.cloud.logging_v2.resource import Resource
from io import StringIO
from typing import Optional

GOOGLE_APPLICATION_CREDENTIALS_ENV_VAR_NAME = "GOOGLE_APPLICATION_CREDENTIALS"
GCP_CREDENTIALS_JSON_ENV_VAR_NAME = "GCP_CREDENTIALS_JSON"


def init_gcp_logger_client(gcp_credentials_path, gcp_credentials_json) -> cloud_logging.Client:
    try:
        if not gcp_credentials_path and not gcp_credentials_json:
            raise ValueError(
                f"Neither {GOOGLE_APPLICATION_CREDENTIALS_ENV_VAR_NAME} nor {GCP_CREDENTIALS_JSON_ENV_VAR_NAME} environment variable is set")

        if gcp_credentials_json:
            # Initialize the client with the provided JSON string
            credentials_dict = json.loads(gcp_credentials_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict)
            client = cloud_logging.Client(credentials=credentials)
        else:
            # Use the default client
            client = cloud_logging.Client()

        return client
    except json.JSONDecodeError:
        raise ValueError(
            f"Invalid JSON in {GCP_CREDENTIALS_JSON_ENV_VAR_NAME} environment variable")
    except Exception as e:
        raise Exception(f"Error setting up GCP logging: {str(e)}")


class GCPLoggingHandler(CloudLoggingHandler):
    def __init__(
            self,
            name: str,
            gcp_credentials_path: Optional[str] = None,
            gcp_credentials_json: Optional[str] = None,
            labels: Optional[dict] = None,
    ):
        client = init_gcp_logger_client(
            gcp_credentials_path or os.environ.get(
                GOOGLE_APPLICATION_CREDENTIALS_ENV_VAR_NAME),
            gcp_credentials_json or os.environ.get(
                GCP_CREDENTIALS_JSON_ENV_VAR_NAME))
        super().__init__(
            client,
            name=name,
            labels=labels,
        )


class GCPExceptionHandler:
    def __init__(self, logger, original_stderr):
        self.logger = logger
        self.original_stderr = original_stderr

    def handle(self, exc_type, exc_value, exc_traceback):
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

        traceback.print_exception(
            exc_type, exc_value, exc_traceback, file=self.original_stderr)


class GCPTextIOWrapper:
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
    handler = GCPLoggingHandler(name=log_name)

    cloud_logger = logging.getLogger(log_name)
    cloud_logger.setLevel(logging.INFO)
    cloud_logger.addHandler(handler)

    original_stderr = sys.stderr

    sys.stdout = GCPTextIOWrapper(cloud_logger)

    exception_handler = GCPExceptionHandler(cloud_logger, original_stderr)
    sys.excepthook = exception_handler.handle
