from typing import Annotated

from eth_typing import ChecksumAddress
from pydantic import BaseModel
from pydantic.functional_validators import AfterValidator
from web3 import Web3

# TODO: This is only for Ethereum, might change if this endpoint starts supporting more chains
Wallet = Annotated[ChecksumAddress, AfterValidator(Web3.to_checksum_address)]


class LeaderboardEntry(BaseModel):
    wallet: Wallet
    total_user_points: int


Leaderboard = list[LeaderboardEntry]


class PointsBreakdown(BaseModel):
    volume: int
    daily: int


class GenerateReferralCodeResponse(BaseModel):
    status: str
    message: str
