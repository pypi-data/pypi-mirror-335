from __future__ import annotations
import abc
from abc import ABC

from ..asset import Token
from ..chain import Chain, EthereumChain, SolanaChain, TronChain
from ..transaction import SentTransaction


class Scanner(ABC):
    __slots__ = tuple()

    @staticmethod
    def create(chain: Chain) -> Scanner:
        match chain:
            case EthereumChain():
                return EIP3091Scanner(chain)
            case SolanaChain():
                return SolanaFM()
            case TronChain():
                return TronScan()
            case _ as chain:
                raise NotImplementedError(f"Unimplemented chain: {chain}")

    @property
    @abc.abstractmethod
    def base_url(self) -> str:
        pass

    @abc.abstractmethod
    def address(self, address: str) -> str:
        pass

    @abc.abstractmethod
    def transaction(self, transaction: SentTransaction) -> str:
        pass

    @abc.abstractmethod
    def token(self, token: Token) -> str:
        pass


# Avoid a circular import
from .eip3091 import EIP3091Scanner  # noqa: E402
from .solana import SolanaFM  # noqa: E402
from .tron import TronScan  # noqa: E402
