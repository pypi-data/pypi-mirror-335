"""
SagaPay Python SDK

This module provides a Python interface to the SagaPay blockchain payment gateway API.
SagaPay is the world's first free, non-custodial blockchain payment gateway service provider.
"""

from .client import Client
from .models import (
    NetworkType,
    TransactionType,
    TransactionStatus,
    AddressType,
    CreateDepositParams,
    CreateWithdrawalParams,
    DepositResponse,
    WithdrawalResponse,
    TransactionStatusResponse,
    WalletBalanceResponse,
    WebhookPayload,
)
from .exceptions import SagaPayError, APIError, ValidationError
from .webhook import WebhookHandler

__version__ = "0.1.0"
__all__ = [
    "Client",
    "NetworkType",
    "TransactionType",
    "TransactionStatus",
    "AddressType",
    "CreateDepositParams",
    "CreateWithdrawalParams",
    "DepositResponse",
    "WithdrawalResponse",
    "TransactionStatusResponse",
    "WalletBalanceResponse",
    "WebhookPayload",
    "SagaPayError",
    "APIError",
    "ValidationError",
    "WebhookHandler",
]