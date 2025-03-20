"""
Helper utilities for WireGuard operations.
"""

import os
import subprocess  # nosec B404
from typing import Dict, Tuple


class WireGuardHelper:
    """Helper class for WireGuard operations."""

    _temp_private_key = ""

    @staticmethod
    def generate_keypair() -> Tuple[str, str]:
        """
        Generate a WireGuard keypair using the wg command.

        Returns:
            Tuple of (private_key: str, public_key: str)
        """
        try:
            # Generate private key
            private_key = subprocess.check_output(
                ["wg", "genkey"], universal_newlines=True
            ).strip()  # nosec B603, B607

            # Store for later use
            WireGuardHelper._temp_private_key = private_key

            # Derive public key
            public_key = subprocess.run(
                ["wg", "pubkey"], input=private_key, text=True, capture_output=True
            ).stdout.strip()  # nosec B603, B607

            return private_key, public_key
        except Exception as e:
            print(f"Error generating WireGuard keypair: {e}")
            return "", ""

    @staticmethod
    def create_client_config(config_data: Dict, output_file: str) -> Tuple[bool, str]:
        """
        Create a WireGuard client configuration file.

        Args:
            config_data: Configuration data from the API
            output_file: Path to save the configuration file

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Extract configuration data
            device_address = config_data.get("device_address")
            server_public_key = config_data.get("server_public_key")
            client_private_key = config_data.get("client_private_key")

            # Check required fields
            if not device_address or not server_public_key:
                return (
                    False,
                    "Missing device_address or server_public_key in API response",
                )

            # If server didn't provide a private key, use our locally generated one
            if not client_private_key:
                client_private_key = WireGuardHelper._temp_private_key
                if not client_private_key:
                    return False, "No private key available"

            # Create configuration file
            config = (
                "[Interface]\n"
                f"PrivateKey = {client_private_key}\n"
                f"Address = {device_address}/24\n"
                "DNS = 1.1.1.1\n\n"
                "[Peer]\n"
                f"PublicKey = {server_public_key}\n"
                "AllowedIPs = 10.8.0.0/24\n"
                "Endpoint = 20.46.55.161:51820\n"
                "PersistentKeepalive = 25\n"
            )

            with open(output_file, "w") as f:
                f.write(config)

            # Set appropriate permissions
            os.chmod(output_file, 0o600)

            return True, f"Configuration saved to {output_file}"
        except Exception as e:
            return False, f"Error creating configuration file: {str(e)}"
