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
from typing import List, Optional
from prime_sdk.credentials import Credentials
from prime_sdk.enums import SizeType
from warnings import warn


@dataclass
class AllocationLeg:
    leg_id: Optional[str] = None
    allocation_leg_id: str
    destination_portfolio_id: str
    amount: str
    allowed_status_codes: List[int] = None

    def __post_init__(self):
        if self.leg_id:
            warn("The 'leg_id' field is deprecated and will be removed in a future version. Use 'allocation_leg_id' instead.", DeprecationWarning)
            self.allocation_leg_id = self.leg_id
        else:
            self.leg_id = self.allocation_leg_id


@dataclass
class CreatePortfolioNetAllocationsRequest:
    allocation_id: str
    source_portfolio_id: str
    product_id: str
    order_ids: List[str]
    allocation_legs: List[AllocationLeg]
    size_type: SizeType
    remainder_destination_portfolio_id: str
    allowed_status_codes: List[int] = None


@dataclass
class CreatePortfolioNetAllocationsResponse(BaseResponse):
    request: CreatePortfolioNetAllocationsRequest


class PrimeClient:
    def __init__(self, credentials: Credentials):
        self.client = Client(credentials)

    def create_portfolio_net_allocations(
            self,
            request: CreatePortfolioNetAllocationsRequest) -> CreatePortfolioNetAllocationsResponse:
        path = "/allocations/net"

        body = asdict(request)
        body['allocation_legs'] = [asdict(leg) for leg in request.allocation_legs]

        response = self.client.request("POST", path, body=body, allowed_status_codes=request.allowed_status_codes)
        return CreatePortfolioNetAllocationsResponse(response.json(), request)
