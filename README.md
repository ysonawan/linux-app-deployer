# Linux Deployer MCP Server

This is a FastMCP server for application deployments on Linux.

## Setup

1. Install Python 3.8+ if not already installed.

2. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Server

Run the server with:
```
fastmcp run main.py
```

Or directly:
```
python main.py
```

## Tools

- `install_package(package_name: str)`: Install a package using apt.
- `run_command(command: str)`: Run a shell command.
- `deploy_docker_container(image: str, name: str = None)`: Deploy a Docker container.

## Note

This server allows running commands on the host Linux system. Use with caution, as it can execute arbitrary commands.
