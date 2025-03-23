from __future__ import annotations
from decimal import Decimal
from typing import Annotated, Optional, TypedDict

from pydantic import AfterValidator, BaseModel

from ..types import MachChain


class ROI(TypedDict):
    times: Decimal
    currency: str
    percentage: Decimal


class AssetInfo(BaseModel):
    id: str
    symbol: Annotated[str, AfterValidator(lambda x: x.upper())]
    name: str
    image: str
    current_price: Decimal
    market_cap: int
    market_cap_rank: Optional[int]
    fully_diluted_valuation: Optional[Decimal]
    total_volume: Decimal
    high_24h: Optional[Decimal]
    low_24h: Optional[Decimal]
    price_change_24h: Optional[Decimal]
    price_change_percentage_24h: Optional[Decimal]
    market_cap_change_24h: Optional[Decimal]
    market_cap_change_percentage_24h: Optional[Decimal]
    circulating_supply: Decimal
    total_supply: Optional[Decimal]
    max_supply: Optional[Decimal]
    ath: Decimal
    ath_change_percentage: Decimal
    ath_date: str
    atl: Decimal
    atl_change_percentage: Decimal
    atl_date: str
    roi: Optional[ROI]
    last_updated: str
    decimals: int

    def __lt__(self, other: AssetInfo) -> bool:
        if not self.market_cap_rank:
            return True
        elif not other.market_cap_rank:
            return False

        return self.market_cap_rank < other.market_cap_rank


class AssetPricingData(BaseModel):
    chain: MachChain
    address: str
    symbol: str
    decimals: int
    price: Decimal
    daily_percent_change: float


class UserAssetData(BaseModel):
    chain: MachChain
    address: str
    balance: int
    symbol: Optional[str] = None
    price: Optional[Decimal]
    daily_percent_change: Optional[Decimal]
