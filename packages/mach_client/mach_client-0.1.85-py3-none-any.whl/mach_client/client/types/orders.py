from enum import Enum
from typing import Optional

from pydantic import BaseModel

from ...chain_client import ChainClient
from ...transaction import SentTransaction
from .types import Chain


class CCTPRequest(BaseModel):
    chain: Chain
    burn_tx: str


class GasResponse(BaseModel):
    gas_estimate: int
    gas_price: int


class OrderRequest(BaseModel):
    chain: Chain
    place_taker_tx: str


class OrderType(str, Enum):
    DEFAULT = "default"
    CCTP = "cctp"


class OrderResponse(BaseModel):
    id: str
    taker_address: str
    maker_address: Optional[str] = None
    src_asset_address: str
    dst_asset_address: str
    src_chain: Chain
    dst_chain: Chain
    src_amount: int
    dst_amount: int
    created_at: str
    filled_at: Optional[str] = None
    expires_at: Optional[str] = None
    completed: bool
    place_tx: str
    fill_tx: Optional[str] = None
    eta: int = 0
    order_type: OrderType = OrderType.DEFAULT

    async def to_sent_transaction(self) -> SentTransaction:
        client = await ChainClient.create(self.src_chain.to_chain())
        return SentTransaction.from_id(client, self.place_tx)
