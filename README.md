# Linux Deployer MCP Server

This is a FastMCP server for managing and deploying applications on Linux systems. It provides a secure, structured interface for running system commands, managing packages, and deploying containerized applications.

## Overview

The Linux Deployer MCP Server is designed to facilitate application deployment workflows through a set of well-defined tools that interact with the host Linux system. This server supports both local development and production deployment scenarios.

### Security Notice

⚠️ **Important**: This server allows executing commands on the host Linux system. Exercise caution when deploying in production environments and ensure proper authentication and authorization controls are in place.

---

## Local Development

This section covers setting up and running the Linux Deployer MCP Server for local development purposes.

### Prerequisites

- Python 3.8 or higher
- `uv` package manager (recommended) or pip

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/ysonawan/linux-app-deployer.git
   cd linux-app-deployer
   ```

2. **Install the `uv` package manager** (recommended for development):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install project dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

   Alternatively, if using pip:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### Running the Server Locally

**Using FastMCP (recommended)**:
```bash
fastmcp run server.py
```

**Direct execution**:
```bash
uv run python server.py
```

### Development Workflow

After starting the server, you can interact with the available tools through the MCP client interface. The server will listen for incoming requests and execute the appropriate tool functions.

For debugging and development purposes, check the logs directory for detailed execution information:
```bash
tail -f logs/app.log
```

---

## Production Deployment

This section provides comprehensive instructions for deploying the Linux Deployer MCP Server in a production environment. The deployment includes setting up the application code, configuring Nginx with SSL, and managing the service using systemd.

### Prerequisites

- Ubuntu/Debian-based Linux server with root or sudo access
- Domain name with DNS configured to point to the server
- Nginx web server installed
- Python 3.8 or higher

### Deployment Architecture

The production deployment architecture consists of:
- **Application Server**: FastMCP server running as a systemd service
- **Reverse Proxy**: Nginx configured with SSL/TLS encryption
- **Service Management**: Systemd for automatic service initialization and monitoring

---

### Step 1: Repository Setup

Clone the application repository to the designated production directory.

**Navigate to the deployment directory and set up the folder structure**:
```bash
cd /opt
sudo mkdir -p mcp/repos
sudo chown $(whoami):$(whoami) mcp
cd mcp
```

**Clone the repository**:
```bash
git clone https://github.com/ysonawan/linux-app-deployer.git
cd linux-app-deployer
```

The application code is now located at `/opt/mcp/linux-app-deployer`.

---

### Step 2: Web Server and SSL Configuration

Configure Nginx as a reverse proxy with SSL/TLS encryption to securely expose the MCP server.

#### 2.1 Verify DNS Resolution

Before setting up SSL, ensure your domain resolves correctly:
```bash
dig mcp.famvest.online +short
```

#### 2.2 Install and Configure Certbot

Install Certbot for automated SSL certificate management:
```bash
sudo apt install -y certbot python3-certbot-nginx
certbot --version
```

#### 2.3 Validate Nginx Configuration

Test the current Nginx setup:
```bash
sudo nginx -t
```

Reload Nginx to apply any pending changes:
```bash
sudo systemctl reload nginx
```

#### 2.4 Obtain SSL Certificate

Obtain an SSL certificate for your domain using Certbot:
```bash
sudo certbot --nginx -d mcp.famvest.online
```

Follow the interactive prompts to configure automatic renewal and other options.

#### 2.5 Deploy Nginx Configuration

Copy the provided Nginx configuration file:
```bash
cd /etc/nginx/sites-available
sudo cp /opt/mcp/linux-app-deployer/prod-deployment-scripts/mcp.famvest.online .
```

Enable the site by setting up symlinks and removing defaults:
```bash
cd /etc/nginx/sites-enabled
sudo rm -f default
sudo ln -sf /etc/nginx/sites-available/mcp.famvest.online mcp.famvest.online
```

#### 2.6 Final Nginx Validation

Verify the updated configuration and reload:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

### Step 3: Application Server Setup

Configure the MCP server application with environment variables and dependencies.

#### 3.1 Environment Configuration

Create a `.env` file from the example template (if available):
```bash
cd /opt/mcp/linux-app-deployer
cp .env.example .env
```

Edit the `.env` file with your production settings:
```bash
nano .env
```

Common configuration parameters:
- `LOG_LEVEL`: Set to `INFO` or `ERROR` for production
- `SERVER_PORT`: Port for the internal server
- `API_KEY`: Secure API key for authentication

#### 3.2 Install the `uv` Package Manager

Install the high-performance `uv` package manager:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Reload your shell environment:
```bash
source ~/.bashrc
# Verify installation
which uv
# Expected output: /root/.local/bin/uv
```

#### 3.3 Install Project Dependencies

Install all Python dependencies using `uv`:
```bash
cd /opt/mcp/linux-app-deployer
uv pip install -r requirements.txt
```

Alternatively, if using traditional pip:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### Step 4: Systemd Service Configuration

Set up the MCP server as a systemd service for automatic startup and monitoring.

#### 4.1 Install Service File

Copy the systemd service configuration:
```bash
sudo cp /opt/mcp/linux-app-deployer/prod-deployment-scripts/mcp-linux-app-deployer.service /etc/systemd/system/
```

#### 4.2 Enable and Start the Service

Reload the systemd daemon to recognize the new service:
```bash
sudo systemctl daemon-reload
```

Enable the service to start automatically on boot:
```bash
sudo systemctl enable mcp-linux-app-deployer.service
```

Start the service:
```bash
sudo systemctl restart mcp-linux-app-deployer.service
```

#### 4.3 Verify Service Status

Check the current status of the service:
```bash
sudo systemctl status mcp-linux-app-deployer.service
```

View recent logs:
```bash
sudo journalctl -u mcp-linux-app-deployer.service -n 50 --no-pager
```

Follow logs in real-time:
```bash
sudo journalctl -u mcp-linux-app-deployer.service -f
```

---

### Deployment Completion

The Linux Deployer MCP Server is now running in production. The application is accessible through your configured domain with SSL/TLS encryption.

**Verify the deployment**:
```bash
curl https://mcp.famvest.online/health
```

**Monitoring**:
- Use `systemctl status` to check service health
- Monitor logs via `journalctl` for debugging
- Configure log rotation if necessary

For ongoing maintenance, update the application periodically:
```bash
cd /opt/mcp/linux-app-deployer
git pull
uv pip install -r requirements.txt
sudo systemctl restart mcp-linux-app-deployer.service
```

---

## Cursor and Claude Desktop Integration

This section explains how to configure the Linux Deployer MCP Server with Cursor or Claude Desktop to enable local AI assistance with deployment tasks.

### Configuration for Cursor

1. **Open Cursor Settings**:
   - Open Cursor and go to `Settings` (or `Cursor` > `Settings` on macOS)
   - Navigate to the `Features` tab and locate the MCP section

2. **Add MCP Server Configuration**:
   
   **Without API Key (if authentication is disabled)**:
   ```json
   "linux-app-deployer": {
     "command": "npx",
     "args": [
       "mcp-remote",
       "https://mcp.famvest.online/mcp"
     ]
   }
   ```

   **With API Key (if authentication is enabled)** - **Recommended Method**:
   ```json
   "linux-app-deployer": {
     "command": "npx",
     "args": [
       "mcp-remote",
       "https://mcp.famvest.online/mcp"
     ],
     "env": {
       "MCP_API_KEY": "your-secret-api-key-here"
     }
   }
   ```
   
   Replace `your-secret-api-key-here` with your actual API key.

3. **Restart Cursor**:
   - Close and reopen Cursor to apply the configuration
   - The MCP server connection will be established automatically

### Configuration for Claude Desktop

1. **Locate Configuration File**:
   - On macOS, the configuration file is located at:
     ```
     ~/Library/Application Support/Claude/claude_desktop_config.json
     ```
   - On Windows, the file is typically at:
     ```
     %APPDATA%\Claude\claude_desktop_config.json
     ```
   - On Linux, the file is typically at:
     ```
     ~/.config/Claude/claude_desktop_config.json
     ```

2. **Edit Configuration File**:
   - Open the `claude_desktop_config.json` file in your text editor
   
   **Without API Key (if authentication is disabled)**:
   ```json
   {
     "mcpServers": {
       "linux-app-deployer": {
         "command": "npx",
         "args": [
           "mcp-remote",
           "https://mcp.famvest.online/mcp"
         ]
       }
     }
   }
   ```

   **With API Key (if authentication is enabled)** - **Recommended Method**:
   ```json
   {
     "mcpServers": {
       "linux-app-deployer": {
         "command": "npx",
         "args": [
           "mcp-remote",
           "https://mcp.famvest.online/mcp"
         ],
         "env": {
           "MCP_API_KEY": "your-secret-api-key-here"
         }
       }
     }
   }
   ```
   
   Replace `your-secret-api-key-here` with your actual API key.

3. **Restart Claude Desktop**:
   - Close and reopen Claude Desktop
   - The MCP server connection will be established automatically

### API Key Setup for Cursor/Claude Desktop

To use the API key with Cursor or Claude Desktop:

1. **Get the API Key**: Contact your system administrator for the secret API key set in the Nginx configuration

2. **Update Your Configuration**: Replace `your-secret-api-key-here` in the config with your actual API key:
   ```json
   "env": {
     "MCP_API_KEY": "your-secret-api-key-here"
   }
   ```

3. **Keep it Secure**: 
   - Store your configuration files with restricted permissions
   - For Claude Desktop: `chmod 600 ~/Library/Application\ Support/Claude/claude_desktop_config.json`
   - For Cursor: Ensure your settings file is not world-readable
   - **DO NOT** commit API keys to version control systems
   - Consider using a `.env` file approach if your config file is shared

### Using the MCP Server in Cursor/Claude Desktop

Once configured, you can interact with the Linux Deployer MCP Server by:
- Mentioning deployment tasks in your conversations
- Asking for help with application deployment workflows
- Requesting system command execution through the available tools
- Getting AI-assisted guidance on deployment best practices

The AI assistant will have access to the tools provided by the Linux Deployer MCP Server and can help you automate and manage your Linux application deployments.

### Troubleshooting Connection Issues

If the MCP server connection is not established:

1. **Verify Network Connectivity**:
   - Ensure your machine can reach `https://mcp.famvest.online`:
     ```bash
     curl https://mcp.famvest.online/health
     ```

2. **Check MCP Server Status**:
   - On the production server, verify the service is running:
     ```bash
     sudo systemctl status mcp-linux-app-deployer.service
     ```

3. **Review Logs**:
   - Check Claude Desktop or Cursor logs for connection errors
   - Review the MCP server logs on the remote machine:
     ```bash
     sudo journalctl -u mcp-linux-app-deployer.service -f
     ```

4. **Verify Configuration Syntax**:
   - Ensure the JSON configuration is properly formatted
   - Reload Cursor or Claude Desktop after making changes

5. **API Key Authentication Issues** (if authentication is enabled):
   - **401 Unauthorized**: The API key is missing or invalid
     - Verify the `MCP_API_KEY` environment variable is set in your config
     - Confirm the API key value matches the one configured in Nginx
     - Test with curl:
       ```bash
       curl -H "X-API-Key: your-actual-api-key" https://mcp.famvest.online/mcp
       ```
   
   - **Connection Fails After Configuration Update**: Configuration changes may not take effect immediately
     - Restart Cursor or Claude Desktop completely (not just close and reopen)
     - Clear any cached data in the application settings
     - Verify the JSON configuration syntax is valid
   
   - **401 Error in Logs**: The API key doesn't match Nginx configuration
     - Double-check that the API key in your Cursor/Claude Desktop config matches the one set in `/etc/nginx/sites-available/mcp.famvest.online`
     - Ensure there are no extra spaces or special characters in the API key

6. **Configuration File Issues**:
   - Verify the JSON syntax is valid (use a JSON validator if unsure)
   - Ensure the file has proper permissions: `chmod 600 ~/path/to/config.json`
   - For Claude Desktop, the exact file path is important—use the full path matching your OS

