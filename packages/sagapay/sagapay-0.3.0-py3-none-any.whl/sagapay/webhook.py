"""Webhook handler for SagaPay notifications."""

import hmac
import hashlib
import json
from typing import Dict, Any, Optional, Union

from pydantic import ValidationError as PydanticValidationError

from .exceptions import WebhookError
from .models import WebhookPayload


class WebhookHandler:
    """Handler for SagaPay webhook notifications."""

    def __init__(self, api_secret: str):
        """Initialize the webhook handler.
        
        Args:
            api_secret: Your SagaPay API secret
            
        Raises:
            WebhookError: If api_secret is empty
        """
        if not api_secret:
            raise WebhookError("API secret is required")
        
        self.api_secret = api_secret

    def process_webhook(
        self, payload: Union[str, bytes, Dict[str, Any]], signature: str
    ) -> WebhookPayload:
        """Process and verify a webhook notification.
        
        Args:
            payload: Webhook payload as string, bytes, or dict
            signature: HMAC signature from 'x-sagapay-signature' header
            
        Returns:
            WebhookPayload: The validated webhook payload
            
        Raises:
            WebhookError: If signature validation fails or payload is invalid
        """
        # Convert dict to JSON string if needed
        if isinstance(payload, dict):
            payload = json.dumps(payload)
            
        # Convert string to bytes if needed
        if isinstance(payload, str):
            payload = payload.encode('utf-8')
            
        # Verify the signature
        if not self.verify_signature(payload, signature):
            raise WebhookError("Invalid webhook signature")
            
        # Parse the payload
        try:
            if isinstance(payload, bytes):
                payload_dict = json.loads(payload.decode('utf-8'))
            else:
                payload_dict = json.loads(payload)
                
            return WebhookPayload.model_validate(payload_dict)
        except json.JSONDecodeError:
            raise WebhookError("Invalid JSON payload")
        except PydanticValidationError as e:
            raise WebhookError(f"Invalid webhook payload format: {str(e)}")

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify the HMAC signature of a webhook payload.
        
        Args:
            payload: Webhook payload
            signature: HMAC signature from 'x-sagapay-signature' header
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        computed_signature = hmac.new(
            key=self.api_secret.encode('utf-8'),
            msg=payload,
            digestmod=hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(computed_signature, signature)