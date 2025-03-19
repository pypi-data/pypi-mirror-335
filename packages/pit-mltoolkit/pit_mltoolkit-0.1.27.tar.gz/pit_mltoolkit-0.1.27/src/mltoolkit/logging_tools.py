#!/usr/bin/env python3
"""
mltoolkit_logging.py

This module provides a configurable logger for ML pipelines that works both locally
and in the cloud. It supports structured logging with custom fields using a JSON formatter,
and integrates with Google Cloud Logging when deployed. This helps data scientists build
and run Docker images locally (with console logs) and, when deployed, have logs aggregated
in Google Cloud Logging.

Usage:
    from mltoolkit_logging import setup_logger, ContextLoggerAdapter
    import os

    # Setup base logger.
    base_logger = setup_logger("ml-pipeline")

    # Define context from environment variables or defaults.
    context = {
         "environment": os.environ.get("ENVIRONMENT", "dev"),
         "operating_company": os.environ.get("OPERATING_COMPANY", "ExampleCorp"),
         "stage": os.environ.get("STAGE", "data-prep")
    }

    # Wrap the base logger to automatically include context.
    logger = ContextLoggerAdapter(base_logger, context)

    logger.info("ML Pipeline stage started")
"""

import os
import logging
import json
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler


class CustomJsonFormatter(logging.Formatter):
    """
    Custom JSON Formatter for structured logging.

    Outputs log records as JSON strings, including standard logging fields
    and any extra fields (e.g., 'environment', 'operating_company', 'stage').
    Includes a stack trace if an exception is logged.
    """
    def format(self, record):
        log_data = {
            "message": record.getMessage(),
            "severity": record.levelname,
            "logger": record.name,
            "timestamp": record.created,
        }
        # Include extra fields if provided.
        for key in ("environment", "operating_company", "stage"):
            if key in record.__dict__:
                log_data[key] = record.__dict__[key]
        if record.exc_info:
            log_data["stack_trace"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


def setup_logger(service_name, log_level=logging.INFO, use_cloud: bool = None):
    """
    Configures and returns a logger that either uses Google Cloud Logging or a local stream handler.

    Determines whether to use Cloud Logging based on the GOOGLE_CLOUD_PROJECT environment variable,
    unless overridden by the use_cloud parameter.
    
    Args:
        service_name (str): Identifier for the service.
        log_level (int, optional): Logging level (default: logging.INFO).
        use_cloud (bool, optional): Forces Cloud Logging (True) or local logging (False).
    
    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(log_level)
    logger.handlers = []  # Clear existing handlers

    if use_cloud is None:
        use_cloud = os.environ.get("GOOGLE_CLOUD_PROJECT") is not None

    if use_cloud:
        try:
            client = google.cloud.logging.Client()
            handler = CloudLoggingHandler(client, name=service_name)
        except Exception as e:
            print(f"Error setting up cloud logging: {e}, falling back to local logging.")
            handler = logging.StreamHandler()
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(CustomJsonFormatter())
    logger.addHandler(handler)
    return logger


class ContextLoggerAdapter(logging.LoggerAdapter):
    """
    LoggerAdapter that automatically injects a logging context.

    Wrap your base logger with this adapter to include additional context (e.g.,
    'environment', 'operating_company', 'stage') in every log message without explicitly
    passing them in each log call.
    """
    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs


if __name__ == '__main__':
    """
    Demonstrates the usage of the mltoolkit logging module.

    Configures the logger for local testing (use_cloud=False), sets up the logging context
    from environment variables (or defaults), and logs both an informational message and an
    exception with a stack trace.
    """
    # Define context from environment variables or defaults.
    context = {
        "environment": os.environ.get("ENVIRONMENT", "dev"),
        "operating_company": os.environ.get("OPERATING_CORP", "ExampleCorp"),
        "stage": os.environ.get("STAGE", "data-prep")
    }
    
    # Setup base logger and wrap it with the adapter.
    base_logger = setup_logger("ml-pipeline", use_cloud=False)
    logger = ContextLoggerAdapter(base_logger, context)
    
    # Log a standard structured message without explicitly specifying extra fields.
    logger.info("ML Pipeline stage started")
    
    # Simulate an exception to capture a stack trace.
    try:
        1 / 0
    except Exception:
        logger.exception("Error during data processing")
    
    print("Logging demo complete. Check your logs locally or in Cloud Logging if deployed.")