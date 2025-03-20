"""
Honeypot Python Client

A simple client for tracking events and user behavior.

Basic Usage:
    from honeypot import Honeypot

    # Initialize with your endpoint
    hp = Honeypot("https://webhook.site/your-endpoint")

    # Track a simple event
    hp.track("Page View")

    # Track with properties
    hp.track("Purchase", {
        "product_id": "123",
        "amount": 99.99,
        "currency": "USD"
    })

With Request Object (Django/Flask):
    # Automatically extracts user agent, IP, and other request data
    hp.with_request(request).track("API Call")

    # With user identification
    hp.with_request(request).identify("user@example.com").track("Login")

    # Check if request is from browser
    if hp.is_browser():
        hp.track("Browser Event")

Path-based Event Tracking:
    # Set up path -> event mapping
    hp = Honeypot("https://webhook.site/your-endpoint")
    hp.event_paths({
        "config": "/api/user/user_config/",
        "feed": "/api/feed/*",  # Wildcard matching
        "profile": "/api/user/profile/"
    })

    # Events will be tracked automatically based on request path
    hp.with_request(request).track()  # Event name determined from path

    # Manual event names still work
    hp.track("custom_event")  # Explicitly named event
"""

import asyncio
import aiohttp
import ipaddress
import logging
from typing import Optional, Dict, Any, Union
from datetime import datetime, timezone
import requests
import base64
import gzip
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import re

__version__ = "0.2.7"

logger = logging.getLogger(__name__)

def is_valid_ip(ip: str) -> bool:
    """Validate if string is a valid IP address."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_private_ip(ip: str) -> bool:
    """Check if IP address is private."""
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False

class Honeypot:
    """
    Honeypot client for tracking events and user behavior.
    
    Attributes:
        endpoint (str): The webhook endpoint to send events to
        user_id (Optional[str]): Current user identifier
        request (Any): Request object (Django/Flask) for extracting metadata
        ip (Optional[str]): IP address override
        event_path_mapping (Optional[Dict[str, str]]): Path to event name mapping
    """

    # Class-level constants for crypto
    NONCE_LENGTH = 12  # AES-GCM nonce size
    SEALED_HEADER = bytes([0x9e, 0x85, 0xdc, 0xed])  # Custom header for validation
    TAG_LENGTH = 16  # AES-GCM tag size (typically 16 bytes)

    def __init__(self, url, api_key=None, api_secret=None):
        # Ensure URL ends with /events
        self.url = url if url.endswith('/events') else f"{url}/events"
        self.api_key = api_key
        self.api_secret = api_secret
        self.user_id = None
        self.request = None
        self.ip = None
        self.event_path_mapping = None

    def with_request(self, request: Any) -> 'Honeypot':
        """Attach request object to extract headers and metadata."""
        self.request = request
        return self

    def identify(self, user_id: str) -> 'Honeypot':
        """Set user identifier for tracking."""
        self.user_id = user_id
        return self

    def set_ip(self, ip: str) -> 'Honeypot':
        """Override IP address for tracking."""
        self.ip = ip
        return self

    def is_browser(self) -> bool:
        """Check if request is from a browser."""
        if not self.request:
            return False
        return bool(self.request.headers.get('Browser-Token'))

    def _get_client_ip(self) -> str:
        """Extract client IP from request object using specified header order"""
        if self.ip:
            return self.ip
            
        if not self.request:
            return ''

        # Headers to check in priority order
        ip_headers = [
            ('CF-Connecting-IP', lambda x: x),
            ('Forwarded', lambda x: next((
                part.split('=', 1)[1].strip().strip('[]').split(':')[0]
                for part in x.replace(' ', '').split(';')
                for sub_part in part.split(',')
                if sub_part.startswith('for=')
            ), None)),
            ('X-Forwarded-For', lambda x: x.split(',')[0].strip()),
            ('Remote-Addr', lambda x: x)
        ]

        first_ip_maybe_private = None

        # Check headers in order
        for header, extractor in ip_headers:
            value = self.request.headers.get(header)
            if not value:
                continue
                
            ip = extractor(value)
            if not ip or not is_valid_ip(ip):
                continue

            if not first_ip_maybe_private:
                first_ip_maybe_private = ip
                
            if not is_private_ip(ip):
                return ip

        return first_ip_maybe_private or ''

    def event_paths(self, path_mapping: Dict[str, str]) -> 'Honeypot':
        """
        Set path to event name mapping for automatic tracking.
        
        Args:
            path_mapping: Dictionary mapping event names to paths
                e.g. {"feed": "/api/feed/*"}
        """
        self.event_path_mapping = path_mapping
        return self

    def _get_event_name_from_path(self) -> Optional[str]:
        """Get event name from request path using configured mapping."""
        if not self.request or not self.event_path_mapping:
            return None
        
        # Split on ? to remove query parameters and normalize path
        path = getattr(self.request, 'path', '').split('?')[0].strip('/')
        # Ensure path starts with /
        path = f"/{path}"
        
        for event_name, pattern in self.event_path_mapping.items():
            # Strip any trailing slashes from the pattern
            pattern = pattern.rstrip('/')
            # Ensure pattern starts with /
            pattern = f"/{pattern.lstrip('/')}"
            
            # Convert glob-style pattern to regex pattern
            if '*' in pattern:
                pattern = pattern.replace('*', '[^/]+')
            # Ensure pattern matches start and end
            pattern = f"^{pattern}/?$"
            
            try:
                if re.match(pattern, path):
                    return event_name
            except re.error:
                logger.debug(f"Invalid regex pattern: {pattern}")
                continue
            
        return None

    def _get_payload(self, event_name: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build event payload with request metadata."""
        payload = {
            'event_name': event_name,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'user_id': self.user_id,
            'client_version': f"honeypot-py/{__version__}",
        }

        if properties:
            payload['event_properties'] = properties

        if self.request:
            # Extract request parameters
            request_params = getattr(self.request, 'GET', {})
            if hasattr(request_params, 'dict'):
                request_params = request_params.dict()

            # Get request body - try different methods depending on framework
            request_body = None
            try:
                # Try to get raw body first
                if hasattr(self.request, 'body'):
                    request_body = self.request.body
                    # If it's bytes, try to decode as JSON
                    if isinstance(request_body, bytes):
                        try:
                            request_body = json.loads(request_body.decode('utf-8'))
                        except json.JSONDecodeError:
                            pass
                # Fall back to POST data if no raw body or couldn't decode
                if request_body is None:
                    request_body = getattr(self.request, 'POST', {})
                    if hasattr(request_body, 'dict'):
                        request_body = request_body.dict()
            except Exception as e:
                logger.debug(f"Error getting request body: {e}")
                request_body = {}

            payload.update({
                'ip_address': self._get_client_ip(),
                'user_agent': self.request.headers.get('User-Agent', ''),
                'browser_token': self.request.headers.get('Browser-Token', ''),
                'device_id': self.request.headers.get('Device-Id', ''),
                'anonymous_id': self.request.headers.get('Anonymous-Id', ''),
                'path': getattr(self.request, 'path', None),
                'method': getattr(self.request, 'method', None),
                'orig_request_params': request_params,
                'orig_request_body': request_body,
                'orig_request_headers': dict(self.request.headers),
            })

        return payload

    async def track_async(
        self,
        event_name_or_properties: Optional[Union[str, Dict[str, Any]]] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Track an event asynchronously in the background.
        """
        # Determine event name and properties based on args
        if isinstance(event_name_or_properties, dict):
            event_props = event_name_or_properties
            event_name = self._get_event_name_from_path()
        else:
            event_name = event_name_or_properties
            event_props = properties

        if not event_name:
            event_name = self._get_event_name_from_path()
            
        if not event_name:
            logger.debug(f"No event name provided and no mapping found for path: {getattr(self.request, 'path', None)}")
            return

        payload = self._get_payload(event_name, event_props)
        headers = {
            'Content-Type': 'application/json',
        }

        if self.api_key and self.api_secret:
            headers['X-API-Key'] = self.api_key
            headers['X-API-Secret'] = self.api_secret

        async def send_request():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.url,
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        response_text = await response.text()
                        logger.debug(f"Response status: {response.status}, body: {response_text}")
            except Exception as e:
                logger.warning(f"Error tracking event: {str(e)}")

        # Create background task
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            except Exception as e:
                logger.debug(f"Failed to create event loop: {e}")
                return

        try:
            loop.create_task(send_request())
        except Exception as e:
            logger.debug(f"Failed to create background task: {e}")

    def track(
        self,
        event_name_or_properties: Optional[Union[str, Dict[str, Any]]] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Track an event synchronously.
        
        Args:
            event_name_or_properties: Either the event name (str) or properties dict
            properties: Additional event properties (only used if first arg is event name)
            
        Returns:
            Optional[Dict[str, Any]]: Dictionary containing response status and body if successful, None if failed
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.track_async(event_name_or_properties, properties))

    @staticmethod
    def _import_key(base64_key: str) -> bytes:
        """Import and decode a base64 key."""
        return base64.b64decode(base64_key)

    @staticmethod
    def _decompress(data: bytes) -> bytes:
        """Decompress gzipped data."""
        return gzip.decompress(data)

    @staticmethod
    def unseal(sealed_base64: str, base64_key: str) -> dict:
        """
        Decrypt and decompress a sealed payload.
        
        Args:
            sealed_base64 (str): Base64 encoded sealed data
            base64_key (str): Base64 encoded encryption key
            
        Returns:
            dict: Decrypted and decompressed payload as dictionary
            
        Raises:
            ValueError: If inputs are invalid or decryption fails
        """
        if not sealed_base64 or not isinstance(sealed_base64, str):
            raise ValueError('Invalid sealedBase64 input')
        if not base64_key or not isinstance(base64_key, str):
            raise ValueError('Invalid base64Key input')

        key = Honeypot._import_key(base64_key)

        try:
            sealed_result = base64.b64decode(sealed_base64)
        except Exception as e:
            raise ValueError('Invalid base64 string') from e

        # Verify the header
        if sealed_result[:len(Honeypot.SEALED_HEADER)] != Honeypot.SEALED_HEADER:
            raise ValueError('Invalid header')

        # Extract nonce, encrypted data, and authentication tag
        nonce = sealed_result[len(Honeypot.SEALED_HEADER):len(Honeypot.SEALED_HEADER) + Honeypot.NONCE_LENGTH]
        encrypted_data_with_tag = sealed_result[len(Honeypot.SEALED_HEADER) + Honeypot.NONCE_LENGTH:]
        encrypted_data = encrypted_data_with_tag[:-Honeypot.TAG_LENGTH]
        tag = encrypted_data_with_tag[-Honeypot.TAG_LENGTH:]

        # Decrypt the data using AES-GCM
        try:
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

            # Decompress the decrypted payload
            decompressed_payload = Honeypot._decompress(decrypted_data)

            # Convert the decompressed payload back to a string and parse as JSON
            decoded_payload = decompressed_payload.decode('utf-8')
            return json.loads(decoded_payload)
        except Exception as e:
            raise ValueError(f'Decryption failed: {e}') from e
