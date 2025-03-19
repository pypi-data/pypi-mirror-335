# Copyright 2025-present Coinbase Global, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
#  limitations under the License.

from dataclasses import dataclass, asdict
from prime_sdk.base_response import BaseResponse
from prime_sdk.client import Client
from typing import Optional, List
from prime_sdk.credentials import Credentials


@dataclass
class Rpc:
    skip_broadcast: Optional[bool] = None
    url: Optional[str] = None


@dataclass
class EvmParams:
    disable_dynamic_gas: Optional[bool] = None
    replaced_transaction_id: Optional[str] = None
    chain_id: Optional[str] = None


@dataclass
class CreateOnchainTransactionRequest:
    portfolio_id: str
    wallet_id: str
    raw_unsigned_txn: str
    rpc: Optional[Rpc] = None
    evm_params: Optional[EvmParams] = None
    allowed_status_codes: List[int] = None



@dataclass
class CreateOnchainTransactionResponse(BaseResponse):
    request: CreateOnchainTransactionRequest


class PrimeClient:
    def __init__(self, credentials: Credentials):
        self.client = Client(credentials)
        
    def create_onchain_transaction(self, request: CreateOnchainTransactionRequest) -> CreateOnchainTransactionResponse:
        path = f"/portfolios/{request.portfolio_id}/wallets/{request.wallet_id}/onchain_transaction"
        body = {k: v for k, v in asdict(request).items() if v is not None}
        response = self.client.request("POST", path, body=body, allowed_status_codes=request.allowed_status_codes)
        return CreateOnchainTransactionResponse(response.json(), request)
