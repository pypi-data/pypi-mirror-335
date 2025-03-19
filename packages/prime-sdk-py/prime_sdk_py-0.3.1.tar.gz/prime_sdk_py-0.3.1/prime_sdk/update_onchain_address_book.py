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
from typing import List
from prime_sdk.credentials import Credentials
from prime_sdk.model import AddressGroup


@dataclass
class UpdateOnchainAddressBookRequest:
    portfolio_id: str
    address_group: AddressGroup
    allowed_status_codes: List[int] = None


@dataclass
class UpdateOnchainAddressBookResponse(BaseResponse):
    request: UpdateOnchainAddressBookRequest


class PrimeClient:
    def __init__(self, credentials: Credentials):
        self.client = Client(credentials)
        
    def update_onchain_address_book(self, request: UpdateOnchainAddressBookRequest) -> UpdateOnchainAddressBookResponse:
        path = f"/portfolios/{request.portfolio_id}/onchain_address_group"
        body = {k: v for k, v in asdict(request).items() if v is not None}
        response = self.client.request("PUT", path, body=body, allowed_status_codes=request.allowed_status_codes)
        return UpdateOnchainAddressBookResponse(response.json(), request)
