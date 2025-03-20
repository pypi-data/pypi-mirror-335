# WireGuard Configuration API Client

A comprehensive client library and CLI tool for interacting with the WireGuard Configuration Distribution API.

[![CI](https://github.com/tiiuae/wg-api-client-lib/actions/workflows/ci.yml/badge.svg)](https://github.com/tiiuae/wg-api-client-lib/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://img.shields.io/pypi/v/wg-api-client.svg)](https://pypi.org/project/wg-api-client/)

## Features

- Complete API client for the WireGuard Configuration Distribution API
- Command-line interface for all API operations
- Automatic token authentication and renewal
- Configuration file support
- WireGuard keypair generation
- WireGuard configuration file creation
- Hardware-based device ID generation for reliable device identification
- Custom device ID support for greater flexibility

## Installation

### From PyPI (Recommended)

```bash
pip install wg-api-client
```

### From Source

```bash
git clone https://github.com/tiiuae/wg-api-client-lib.git
cd wg-api-client-lib
pip install -e .
```

### Prerequisites for Ubuntu

```bash
sudo apt update
sudo apt install -y python3 python3-pip wireguard-tools
```

## Usage

### As a Command-Line Tool

The package installs a `wg-api-client` command that can be used to interact with the API:

```bash
# Show help
wg-api-client --help

# Authenticate with the API
wg-api-client auth

# Get a WireGuard configuration (device ID is automatically generated from hardware information)
wg-api-client get-config --output mydevice.conf

# Use a custom device ID instead of hardware-based generation
wg-api-client get-config --device-id "custom-id-123" --output mydevice.conf
```

### As a Library

```python
from wg_api_client import WireGuardAPI, WireGuardHelper
from wg_api_client.unique_id import get_unique_device_id

# Initialize the API client
api = WireGuardAPI(
    api_url="your-api_url",
    hashed_credential="your-hashed-credential"
)

# Authenticate
success, _ = api.authenticate()
if success:
    # Generate a device ID based on hardware information
    device_id = get_unique_device_id()
    
    # Or use a custom device ID
    # device_id = "custom-id-123"
    
    # Generate a keypair
    private_key, public_key = WireGuardHelper.generate_keypair()
    
    # Request a configuration
    success, config_data = api.request_wireguard_config(
        device_id=device_id,
        role="drone",
        public_key=public_key
    )
    
    if success:
        # Create a configuration file
        WireGuardHelper.create_client_config(config_data, "wg.conf")
```

## Configuration

The tool stores configuration in `~/.wg_api_config` by default. You can specify a different location with the `--config-file` parameter.

## Available Commands

### Global Parameters

These parameters can be used with any command:

- `--api-url`: Base URL for the API
- `--hashed-credential`: Hashed credential for authentication
- `--config-file`: Path to configuration file (default: ~/.wg_api_config)

### Authentication

```bash
wg-api-client auth
```

This will:
- Authenticate with the API using the hashed credential
- Store the JWT token in the configuration file
- Store the refresh token for automatic token renewal

### Device Configuration Management

#### Get WireGuard Configuration

```bash
wg-api-client get-config [--role {drone|fmo}] [--device-id ID] [--public-key KEY] [--output FILE]
```

Parameters:
- `--role`: Device role - either "drone" or "fmo" (default: "drone")
- `--device-id`: Custom device ID (if not provided, automatically generated based on hardware)
- `--public-key`: WireGuard public key (if not provided, a new keypair will be generated)
- `--output`: Output configuration file (default: "wg.conf")

Examples:

```bash
# Generate a new keypair and configuration with hardware-based device ID
wg-api-client get-config

# Set role to FMO and use an existing public key
wg-api-client get-config --role fmo --public-key "AbCdEf123..." --output fmo.conf

# Use a custom device ID for better tracking and management
wg-api-client get-config --device-id "drone-building-a-floor-3" --output drone-a3.conf

# Combine custom ID with specific role
wg-api-client get-config --role fmo --device-id "fmo-main-control" --output fmo-main.conf
```

#### List All Devices (Admin only)

```bash
wg-api-client list-devices
```

This will display detailed information about all devices, including:
- Device ID
- Role
- IP address
- Public key
- Creation and update timestamps

#### Get Device Information (Admin only)

```bash
wg-api-client get-device DEVICE_ID
```

#### Delete a Device (Admin only)

```bash
wg-api-client delete-device DEVICE_ID
```

#### Delete All Devices (Admin only)

```bash
wg-api-client delete-all-devices [--confirm]
```

Use the `--confirm` flag to bypass the confirmation prompt.

### FMO-specific Operations

#### Get FMO Device Information (Admin only)

```bash
wg-api-client get-fmo
```

#### Remove FMO Role (Admin only)

```bash
wg-api-client delete-fmo
```

### Credential Management (Admin only)

#### Add a New Credential

```bash
wg-api-client add-credential --hashed-credential HASH [--role {user|admin}]
```

Parameters:
- `--hashed-credential`: Hashed credential to add (required)
- `--role`: Role for the credential - either "user" or "admin" (default: "user")

## Examples of Common Workflows

### Setting Up a New Drone Device

```bash
# Authenticate with the API
wg-api-client auth

# Generate a WireGuard configuration with hardware-based device ID
wg-api-client get-config --output drone.conf

# Or use a descriptive custom ID for better device management
wg-api-client get-config --device-id "drone-inspection-team-1" --output drone-team1.conf

# Transfer the generated configuration file to the device and apply it using the WireGuard tools
```

### Setting Up an FMO Device

```bash
# Authenticate with the API
wg-api-client auth

# Check if there's already an FMO device
wg-api-client get-fmo

# If needed, remove the current FMO role
wg-api-client delete-fmo

# Generate a WireGuard configuration for the new FMO device
wg-api-client get-config --role fmo --output fmo.conf

# Or use a meaningful custom ID for your FMO
wg-api-client get-config --role fmo --device-id "fmo-ground-station-1" --output fmo-gs1.conf
```

### Administrator Tasks

```bash
# Check all registered devices
wg-api-client list-devices

# Add a new admin credential
wg-api-client add-credential --hashed-credential "your-hashed-credential" --role admin

# Clean up old devices
wg-api-client delete-device old-device-id
```

## Device ID Generation

The client can use either a custom device ID provided by you or generate a unique device ID based on hardware information. 

### Custom Device ID

Using custom device IDs provides several benefits:
- More descriptive and meaningful names for easier management
- Ability to align device IDs with your organization's naming conventions
- Better tracking across deployments and environments
- Independence from hardware changes that might affect auto-generated IDs

### Auto-generated Device ID

When no custom ID is provided, the client generates a unique device ID based on hardware information. The ID generation follows this priority:

1. eth0 MAC address (on Linux systems)
2. Primary network interface MAC address
3. Any available physical network interface MAC address
4. MAC address from uuid.getnode()
5. Machine UUID from OS-specific sources
6. Fallback to machine-specific information

This ensures each device gets a stable, unique identifier that persists across reboots and reinstallations of the software.

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/tiiuae/wg-api-client-lib.git
cd wg-api-client-lib

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

### Run Tests

```bash
pytest
```

### Run Linters

```bash
# Format code with Black
black .

# Sort imports
isort .

```

## Publishing

This package is available on PyPI and can be automatically published through GitHub releases.

### Automatic Publishing

1. Update version numbers in:
   - `wg_api_client/__init__.py` (`__version__` variable)
   - `setup.py` (`version` parameter)

2. Create a new GitHub release:
   - Go to the GitHub repository
   - Click "Releases" → "Create a new release"
   - Tag version should be in format `v{version}` (e.g., `v0.1.2`)
   - The GitHub Action will automatically build and publish to PyPI

### Manual Publishing

For detailed instructions on manual publishing, see [PUBLISHING.md](PUBLISHING.md).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.