"""
Configuration settings for the FastAPI server.
Can be customized via environment variables.
"""
import os
from pathlib import Path

# Server Settings
API_HOST = os.getenv("API_HOST", "127.0.0.1")  # Listen only on localhost for nginx
API_PORT = int(os.getenv("API_PORT", 8002))
API_RELOAD = os.getenv("API_RELOAD", "false").lower() == "true"

# CORS Settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
CORS_CREDENTIALS = os.getenv("CORS_CREDENTIALS", "true").lower() == "true"
CORS_METHODS = os.getenv("CORS_METHODS", "*").split(",")
CORS_HEADERS = os.getenv("CORS_HEADERS", "*").split(",")

# Request/Response Settings
MAX_LINES_LIMIT = int(os.getenv("MAX_LINES_LIMIT", 10000))
MIN_LINES_LIMIT = int(os.getenv("MIN_LINES_LIMIT", 1))
DEFAULT_LINES = int(os.getenv("DEFAULT_LINES", 100))

# Logging Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = Path(os.getenv("LOG_FILE", "/opt/mcp/linux-app-deployer/linux-deployer-api.log"))

# API Settings
API_TITLE = "Linux App Deployer API"
API_DESCRIPTION = "REST API for Linux application deployment tools"
API_VERSION = "1.0.0"

# Feature Flags
ENABLE_CORS = os.getenv("ENABLE_CORS", "true").lower() == "true"
ENABLE_WORKFLOW_ENDPOINTS = os.getenv("ENABLE_WORKFLOW_ENDPOINTS", "true").lower() == "true"
ENABLE_MONITORING_ENDPOINTS = os.getenv("ENABLE_MONITORING_ENDPOINTS", "true").lower() == "true"