# MLToolkit

Welcome to the **MLToolkit** repository! This repository contains tools, functions, and utilities to streamline and optimize workflows for machine learning engineers, data scientists, and analysts. Our toolkit is designed to support end-to-end ML pipelines with modules for artifact management, configuration loading, Docker tooling, GCP bucket operations, and robust logging.

## Table of Contents

- [Overview](#overview)
- [Modules](#modules)
  - [Artifact Registry Tools](#artifact-registry-tools)
  - [Configuration Loader](#configuration-loader)
  - [Docker Tools](#docker-tools)
  - [GCP Bucket Tools](#gcp-bucket-tools)
  - [Logging Utilities](#logging-utilities)
- [Installation](#installation)
- [Usage](#usage)
- [Contributors](#contributors)

## Overview

**MLToolkit** is a comprehensive collection of scripts, functions, and libraries designed to streamline the workflows for managing, deploying, and monitoring machine learning models. The toolkit currently includes:

- **Artifact Management:**  
  Utilities for interacting with Google Cloud Artifact Registry to version and manage model artifacts.
- **Configuration Handling:**  
  Modules for loading and parsing configuration files from local storage or GCP buckets.
- **Container & Docker Tools:**  
  Functions for building, running, and managing Docker images to support containerized ML workflows.
- **Cloud Storage Utilities:**  
  Tools to manage Google Cloud Storage buckets for file uploads, downloads, and bucket operations.
- **Robust Logging & Monitoring:**  
  A configurable logging solution that works both locally and in the cloud, providing structured JSON logs for effective monitoring and debugging.

**Future Enhancements:**

- **Extended Cloud Integration:**  
  Expanding support to additional cloud providers (e.g., AWS, Azure) and deeper integration with production ML pipelines.
- **Advanced Pipelines & Version Control:**  
  Enhanced pipelines for model training, evaluation, and deployment, along with integrated version control for model management.
- **Enhanced Monitoring & Debugging:**  
  More sophisticated tools for real-time monitoring, debugging, and alerting to ensure robust production deployments.


It is built to work seamlessly both locally and in the cloud, ensuring that logs, artifacts, and configurations are consistent and centralized.

## Modules

### Artifact Registry Tools (`artifact_registry_tools.py`)

This module provides the `ArtifactHelper` class to interact with Google Cloud Artifact Registry. It supports operations such as checking for existing repositories, creating new repositories, listing repositories, and uploading files.

**Usage Example:**
```python
from mltoolkit import artifact_registry_tools

helper = artifact_registry_tools.ArtifactHelper(
    project_id="your-project",
    location="your-location",
    credential_file_path="path/to/creds.json"
)

if helper.check_repository("my-repo"):
    print("Repository exists")
else:
    helper.create_repository("my-repo", repository_format="docker")
```

### Configuration Loader (`config_loader.py`)

The ConfigLoader class supports loading configuration files (YAML, YML, and JSON) either from a local path or directly from a GCP bucket.

**Usage Example:**
```python
from mltoolkit import config_loader

loader = config_loader.ConfigLoader()
config = loader.load_from_bucket("my-bucket", "config.yaml")
print(config)
```

### Docker Tools (`docker_tools.py`)

The DockerTool class offers utility functions for building, deleting, running, listing, and uploading Docker images. It also supports cleaning up Docker resources to manage storage.

**Usage Example:**
```python
from mltoolkit import docker_tools

docker = docker_tools.DockerTool(credentials_file_path="path/to/creds.json")
docker.build_image(image_name="my-image", dockerfile="Dockerfile")
```

### GCP Bucket Tools (`gcp_bucket.py`)

**Usage Example:**
```python
from mltoolkit import gcp_bucket

bucket = gcp_bucket.GCPBucket(
    project_id="your-project",
    location="your-location",
    credentials="path/to/creds.json",
    bucket_name="my-bucket"
)
bucket.local_file_upload("local_file.txt", "uploads/file.txt")
```

### Logging Utilities (`logging.py`)

The `mltoolkit_logging.py` module now supports a logging methodology that automatically injects structured context (such as environment, operating company, and stage) into every log entry. Using the ContextLoggerAdapter, you can define your logging context once—via environment variables or a configuration file—and have it applied automatically, reducing repetition and potential errors.

#### Setup

Import both the base logger setup and the `ContextLoggerAdapter` from the package. Define your default context and wrap your logger with the adapter. For example, for local testing you might force local logging:

```python
from mltoolkit import logging
import os

# Setup the base logger; for local testing, force local logging with use_cloud=False.
base_logger = logging.setup_logger("ml-pipeline", use_cloud=False)

# Define default context from environment variables or fallback values.
context = {
    "environment": os.environ.get("ENVIRONMENT", "dev"),
    "operating_company": os.environ.get("OPERATING_CORP", "ExampleCorp"),
    "stage": os.environ.get("STAGE", "data-prep")
}

# Wrap the base logger with the LoggerAdapter to automatically inject context.
logger = logging.ContextLoggerAdapter(base_logger, context)
```

#### Logging at Various Levels

**Logging at Various Levels**
Once configured, you can log messages without explicitly specifying the extra context. The adapter automatically merges your default context into each log record.

- **DEBUG:** Detailed system information for diagnosing issues.
```python
  logger.debug("DEBUG: Detailed debug message for initialization.")
```

- **INFO:** General process information.
```python
logger.info("INFO: Process started successfully.")
```

- **WARNING:** Indicates a potential issue that doesn't stop execution.
```python
logger.warning("WARNING: Detected a potential issue in data preprocessing.")
```

- **ERROR:** Logs an error that occurred during execution.
```python
logger.error("ERROR: Failed to train model due to invalid input.", exc_info=True)
```

- **CRITICAL:** Logs a severe error with a stack trace.
```python
  try:
      1 / 0  # Simulate an error.
  except Exception:
      logger.critical("CRITICAL: Fatal error during model deployment.", exc_info=True)
```

**Overriding or Extending Context**
If needed, you can still pass an extra dictionary to override or add additional context for a specific log entry. This extra data will be merged with the default context:

```python
  logger.info("Custom log message with additional context.", extra={"stage": "custom-stage"})
```

These examples demonstrate how to log at different severity levels with structured metadata. When deployed (by setting use_cloud=True), logs will be sent to Google Cloud Logging, allowing you to aggregate logs across different projects and environments.

#### Installation

**Clone the repository and install the required dependencies:**
```bash
pip install pit-mltoolkit
```

#### Usage
**Import the modules as needed in your projects:**
```python
from mltoolkit import artifact_registry_tools, config_loader, docker_tools, gcp_bucket, logging
```

Refer to the examples provided in each module section above for guidance on how to integrate these utilities into your ML workflows.

#### Contributors

- PepkorIT Machine Learning Engineering Team:
    - Tyron Lambrechts
    - Thomas Verryne
    - Neil Slabbert