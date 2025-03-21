"""SagaPay API client implementation."""

import json
from typing import Dict, Optional, Any, Union, List, Type, TypeVar

import requests
from pydantic import ValidationError as PydanticValidationError

from .exceptions import ValidationError, APIError, NetworkError, SagaPayError
from .models import (
    CreateDepositParams,
    CreateWithdrawalParams,
    DepositResponse,
    WithdrawalResponse,
    TransactionStatusResponse,
    WalletBalanceResponse,
    NetworkType,
    TransactionType,
)

T = TypeVar("T")


class Client:
    """SagaPay API client."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "https://api2.sagapay.net",
        timeout: int = 30,
    ):
        """Initialize the SagaPay client.
        
        Args:
            api_key: Your SagaPay API key
            api_secret: Your SagaPay API secret
            base_url: Base URL for the SagaPay API
            timeout: Request timeout in seconds
        
        Raises:
            ValidationError: If api_key or api_secret are empty
        """
        if not api_key:
            raise ValidationError("API key is required")
        if not api_secret:
            raise ValidationError("API secret is required")

        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def create_deposit(self, params: Union[Dict[str, Any], CreateDepositParams]) -> DepositResponse:
        """Create a deposit address for receiving cryptocurrency.
        
        Args:
            params: Parameters for creating a deposit
        
        Returns:
            DepositResponse: Response containing deposit information
        
        Raises:
            ValidationError: If the parameters are invalid
            APIError: If the API returns an error
            NetworkError: If the request fails
        """
        if not isinstance(params, CreateDepositParams):
            try:
                params = CreateDepositParams(**params)
            except PydanticValidationError as e:
                errors = e.errors()
                if errors:
                    field = errors[0]["loc"][0] if "loc" in errors[0] and errors[0]["loc"] else None
                    message = errors[0]["msg"] if "msg" in errors[0] else str(e)
                    raise ValidationError(message, field)
                raise ValidationError(str(e))

        return self._post("/create-deposit", params.dict(exclude_none=True), DepositResponse)

    def create_withdrawal(
        self, params: Union[Dict[str, Any], CreateWithdrawalParams]
    ) -> WithdrawalResponse:
        """Create a withdrawal request.
        
        Args:
            params: Parameters for creating a withdrawal
        
        Returns:
            WithdrawalResponse: Response containing withdrawal information
        
        Raises:
            ValidationError: If the parameters are invalid
            APIError: If the API returns an error
            NetworkError: If the request fails
        """
        if not isinstance(params, CreateWithdrawalParams):
            try:
                params = CreateWithdrawalParams(**params)
            except PydanticValidationError as e:
                errors = e.errors()
                if errors:
                    field = errors[0]["loc"][0] if "loc" in errors[0] and errors[0]["loc"] else None
                    message = errors[0]["msg"] if "msg" in errors[0] else str(e)
                    raise ValidationError(message, field)
                raise ValidationError(str(e))

        return self._post("/create-withdrawal", params.dict(exclude_none=True), WithdrawalResponse)

    def check_transaction_status(
        self, address: str, transaction_type: Union[str, TransactionType]
    ) -> TransactionStatusResponse:
        """Check the status of transactions for a specific address.
        
        Args:
            address: Blockchain address to check
            transaction_type: Type of transaction ("deposit" or "withdrawal")
        
        Returns:
            TransactionStatusResponse: Response containing transaction status information
        
        Raises:
            ValidationError: If the parameters are invalid
            APIError: If the API returns an error
            NetworkError: If the request fails
        """
        if not address:
            raise ValidationError("Address is required")

        if isinstance(transaction_type, str):
            try:
                transaction_type = TransactionType(transaction_type)
            except ValueError:
                raise ValidationError(
                    f"Invalid transaction type. Must be one of: {', '.join([t.value for t in TransactionType])}"
                )

        params = {"address": address, "type": transaction_type.value}
        return self._get("/check-transaction-status", params, TransactionStatusResponse)

    def fetch_wallet_balance(
        self,
        address: str,
        network_type: Union[str, NetworkType],
        contract_address: Optional[str] = None,
    ) -> WalletBalanceResponse:
        """Fetch the balance of a specific wallet address.
        
        Args:
            address: Blockchain address to check
            network_type: Type of blockchain network
            contract_address: Contract address for the token (optional, use "0" for native currency)
        
        Returns:
            WalletBalanceResponse: Response containing wallet balance information
        
        Raises:
            ValidationError: If the parameters are invalid
            APIError: If the API returns an error
            NetworkError: If the request fails
        """
        if not address:
            raise ValidationError("Address is required")

        if isinstance(network_type, str):
            try:
                network_type = NetworkType(network_type)
            except ValueError:
                raise ValidationError(
                    f"Invalid network type. Must be one of: {', '.join([t.value for t in NetworkType])}"
                )

        params = {"address": address, "networkType": network_type.value}
        if contract_address:
            params["contractAddress"] = contract_address

        return self._get("/fetch-wallet-balance", params, WalletBalanceResponse)

    def _get(self, path: str, params: Dict[str, Any], response_type: Type[T]) -> T:
        """Send a GET request to the API.
        
        Args:
            path: API endpoint path
            params: Query parameters
            response_type: Response model type
        
        Returns:
            The response model instance
        
        Raises:
            APIError: If the API returns an error
            NetworkError: If the request fails
        """
        return self._request("GET", path, params=params, response_type=response_type)

    def _post(self, path: str, data: Dict[str, Any], response_type: Type[T]) -> T:
        """Send a POST request to the API.
        
        Args:
            path: API endpoint path
            data: Request body data
            response_type: Response model type
        
        Returns:
            The response model instance
        
        Raises:
            APIError: If the API returns an error
            NetworkError: If the request fails
        """
        return self._request("POST", path, json=data, response_type=response_type)

    def _request(
        self,
        method: str,
        path: str,
        response_type: Type[T],
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> T:
        """Send a request to the API.
        
        Args:
            method: HTTP method
            path: API endpoint path
            response_type: Response model type
            params: Query parameters
            json: JSON body data
        
        Returns:
            The response model instance
        
        Raises:
            APIError: If the API returns an error
            NetworkError: If the request fails
        """
        url = f"{self.base_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": self.api_key,
            "x-api-secret": self.api_secret,
        }

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                timeout=self.timeout,
            )
            response.raise_for_status()
            
            try:
                response_data = response.json()
            except ValueError:
                raise APIError("Invalid JSON response")

            try:
                return response_type.model_validate(response_data)
            except PydanticValidationError as e:
                raise APIError(f"Invalid response format: {str(e)}")

        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get("message", str(e))
                error_code = error_data.get("error")
                raise APIError(
                    message=error_message,
                    status_code=e.response.status_code,
                    error_code=error_code,
                    response=error_data,
                )
            except (ValueError, AttributeError):
                raise APIError(
                    message=str(e),
                    status_code=e.response.status_code if hasattr(e, "response") else None,
                )

        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}", e)