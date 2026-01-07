# Linux App Deployer API Endpoints

This document lists the REST API endpoints exposed by the `api.py` FastAPI server for the Linux App Deployer.

## Health & Info Endpoints
- **GET /health**  
  Health check endpoint. Returns `{"status": "healthy"}`.

- **GET /**  
  Root endpoint with API information, including service name, version, docs link, and status.

## Configuration Endpoints
- **GET /api/v1/configuration**  
  Retrieves application deployment configuration and available applications.

## Repository Operations
- **POST /api/v1/repository/checkout/{application_name}**  
  Clones or updates the repository for the specified application.

## Build Operations
- **POST /api/v1/build/application/{application_name}**  
  Builds the application using the predefined build system.

- **POST /api/v1/artifact/verify/{application_name}**  
  Verifies that the build artifact exists and is non-empty.

## Deployment Operations
- **POST /api/v1/deployment/deploy/{application_name}**  
  Deploys the artifact to the deployment directory with backup.

- **POST /api/v1/application/restart/{application_name}**  
  Restarts the systemd service for the application.

- **POST /api/v1/application/stop/{application_name}**  
  Stops the systemd service for the application.

## Status & Monitoring
- **GET /api/v1/application/status/{application_name}**  
  Retrieves the systemd service status for the application.

- **GET /api/v1/application/logs/{application_name}**  
  Fetches recent logs for the application service. Supports query parameter `lines` (default 100, max 10000).

- **GET /api/v1/running-services**  
  Retrieves list of running systemd services on the server.

- **GET /api/v1/server-health-summary**  
  Fetches server health summary including CPU, memory, disk usage, and load average.

## Workflow Endpoints
- **POST /api/v1/deployment/workflow/full-deploy/{application_name}**  
  Executes the full deployment workflow: checkout → build → verify → deploy → restart → status.