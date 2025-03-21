"""Models for the SagaPay SDK."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union

from pydantic import BaseModel, Field


class NetworkType(str, Enum):
    """Supported blockchain network types."""
    
    ERC20 = "ERC20"
    BEP20 = "BEP20"
    TRC20 = "TRC20"
    POLYGON = "POLYGON"
    SOLANA = "SOLANA"


class TransactionType(str, Enum):
    """Transaction types."""
    
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class TransactionStatus(str, Enum):
    """Transaction statuses."""
    
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AddressType(str, Enum):
    """Address types."""
    
    TEMPORARY = "TEMPORARY"
    PERMANENT = "PERMANENT"


class CreateDepositParams(BaseModel):
    """Parameters for creating a deposit."""
    
    network_type: NetworkType
    contract_address: str
    amount: str
    ipn_url: str
    udf: Optional[str] = None
    type: Optional[AddressType] = None
    
    class Config:
        """Pydantic model configuration."""
        
        populate_by_name = True
        
    def dict(self, *args, **kwargs):
        """Convert the model to a dictionary with proper field names."""
        data = super().dict(*args, **kwargs)
        # Convert camelCase for API compatibility
        if "ipn_url" in data:
            data["ipnUrl"] = data.pop("ipn_url")
        return data


class CreateWithdrawalParams(BaseModel):
    """Parameters for creating a withdrawal."""
    
    network_type: NetworkType
    contract_address: str
    address: str
    amount: str
    ipn_url: str
    udf: Optional[str] = None
    
    class Config:
        """Pydantic model configuration."""
        
        populate_by_name = True
    
    def dict(self, *args, **kwargs):
        """Convert the model to a dictionary with proper field names."""
        data = super().dict(*args, **kwargs)
        # Convert camelCase for API compatibility
        if "ipn_url" in data:
            data["ipnUrl"] = data.pop("ipn_url")
        return data


class DepositResponse(BaseModel):
    """Response from creating a deposit."""
    
    id: str
    address: str
    expires_at: datetime = Field(alias="expiresAt")
    amount: str
    status: TransactionStatus


class WithdrawalResponse(BaseModel):
    """Response from creating a withdrawal."""
    
    id: str
    status: TransactionStatus
    fee: str


class Token(BaseModel):
    """Token information."""
    
    network_type: NetworkType = Field(alias="networkType")
    contract_address: str = Field(alias="contractAddress")
    symbol: str
    name: str
    decimals: int


class Balance(BaseModel):
    """Balance information."""
    
    raw: str
    formatted: str


class Transaction(BaseModel):
    """Transaction details."""
    
    id: str
    transaction_type: TransactionType = Field(alias="transactionType")
    status: TransactionStatus
    amount: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    tx_hash: Optional[str] = Field(default=None, alias="txHash")
    network_type: NetworkType = Field(alias="networkType")
    contract_address: str = Field(alias="contractAddress")
    address: str
    token: Token


class TransactionStatusResponse(BaseModel):
    """Response from checking transaction status."""
    
    address: str
    transaction_type: TransactionType = Field(alias="transactionType")
    count: int
    transactions: List[Transaction]


class WalletBalanceResponse(BaseModel):
    """Response from fetching wallet balance."""
    
    address: str
    network_type: NetworkType = Field(alias="networkType")
    contract_address: str = Field(alias="contractAddress")
    token: Token
    balance: Balance


class WebhookPayload(BaseModel):
    """Webhook payload sent in notifications."""
    
    id: str
    type: TransactionType
    status: TransactionStatus
    address: str
    network_type: NetworkType = Field(alias="networkType")
    amount: str
    udf: Optional[str] = None
    tx_hash: Optional[str] = Field(default=None, alias="txHash")
    timestamp: datetime