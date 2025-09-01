"""
Invoice Service Integration Settings
"""
import os
from decouple import config

# Invoice Service gRPC Configuration
INVOICE_SERVICE_HOST = config('INVOICE_SERVICE_HOST', default='localhost')
INVOICE_SERVICE_PORT = config('INVOICE_SERVICE_PORT', default='50055')
INVOICE_SERVICE_TIMEOUT = config('INVOICE_SERVICE_TIMEOUT', default='10s')

# Invoice Service Features
INVOICE_SERVICE_ENABLED = config('INVOICE_SERVICE_ENABLED', default=True, cast=bool)
INVOICE_SERVICE_FALLBACK_ENABLED = config('INVOICE_SERVICE_FALLBACK_ENABLED', default=True, cast=bool)

# Document Generation Settings
INVOICE_DEFAULT_FORMAT = config('INVOICE_DEFAULT_FORMAT', default='pdf')
INVOICE_DEFAULT_TEMPLATE = config('INVOICE_DEFAULT_TEMPLATE', default=None)

# Cache Settings for Invoice Service
INVOICE_SERVICE_CACHE_TTL = config('INVOICE_SERVICE_CACHE_TTL', default=300, cast=int)  # 5 minutes

# Logging Configuration for Invoice Service
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'invoice_service': {
            'format': '[{levelname}] {asctime} - Invoice Service - {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'invoice_service_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/invoice_service.log',
            'formatter': 'invoice_service',
        },
        'invoice_service_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'invoice_service',
        },
    },
    'loggers': {
        'grpc_clients.invoice_client': {
            'handlers': ['invoice_service_file', 'invoice_service_console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Update main logging configuration
import logging.config
logging.config.dictConfig(LOGGING_CONFIG)