from __future__ import annotations
import typing

from ..asset import Token
from ..transaction import SolanaSentTransaction
from .scanner import Scanner


class SolanaFM(Scanner):
    __slots__ = tuple()

    url = "https://solana.fm"

    @property
    @typing.override
    def base_url(self) -> str:
        return self.url

    @typing.override
    def address(self, address: str) -> str:
        return f"{self.url}/address/{address}"

    @typing.override
    def transaction(self, transaction: SolanaSentTransaction) -> str:
        return f"{self.url}/tx/{transaction.id}"

    @typing.override
    def token(self, token: Token) -> str:
        return self.address(token.address)
