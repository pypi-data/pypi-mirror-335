# gcp-lolo

GCP Cloud Logging Python logger

The idea behind this package is to provide the simplest way to log messages to Google Cloud Logging, without having to worry about the details of setting up the Google Cloud Logging client and/or affecting the current application structure.

## Installation

```bash
pip install gcp-lolo
```

## Usage

### Prerequisites

Be sure either one of the following environment variables is set

- `GOOGLE_APPLICATION_CREDENTIALS`, pointing to the path of the GCP credentials JSON file
- `GCP_CREDENTIALS_JSON`, a string containing the GCP credentials JSON file

### Usage method #1

```python
from gcp_lolo import get_gcp_logger

logger = get_gcp_logger('my-logger')

logger.info('This is a test info message')
logger.error('This is a test error message')
```

### Usage method #2

This method will redirect all `print` and `raise` statements to the GCP logger, so that you can avoid the need to change your code to use the logger directly.

```python
from gcp_lolo import setup_gcp_logging


setup_gcp_logging('my-logger')

print('This is a test message')

raise Exception('This is a test exception')
```
