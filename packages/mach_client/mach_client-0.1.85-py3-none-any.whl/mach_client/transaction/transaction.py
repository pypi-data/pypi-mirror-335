from __future__ import annotations
import abc
from abc import ABC
import dataclasses
from typing import Any

from hexbytes import HexBytes
from solders.signature import Signature
from tronpy.async_tron import AsyncTransactionRet

from ..chain import Chain
from ..chain_client import ChainClient, EthereumClient, SolanaClient, TronClient


# Proxy for a chain-specific sent transaction
@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class SentTransaction[ChainType: Chain](ABC):
    @classmethod
    def from_id(
        cls, client: ChainClient[ChainType], id: str
    ) -> SentTransaction[ChainType]:
        match client:
            case EthereumClient():
                return ethereum.EthereumSentTransaction(
                    client=client,
                    transaction_hash=HexBytes(id),
                )

            case SolanaClient():
                return solana.SolanaSentTransaction(
                    client=client,
                    signature=Signature.from_string(id),
                )

            case TronClient():
                return tron.TronSentTransaction(
                    chain_=client.chain,
                    native=AsyncTransactionRet(
                        iterable=(("txid", id),), client=client.native
                    ),
                )

            case _:
                raise NotImplementedError(f"Unimplemented chain: {client.chain}")

    # TODO: This currently doesn't follow the convention in the rest of the codebase that the `.id` property should produce a CAIP identifier that is unique across chains. Instead we return the transaction hash or equivalent, which is not necessarily unique across chains.
    @property
    @abc.abstractmethod
    def id(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def chain(self) -> ChainType:
        pass

    # Confirms the transaction if necessary and returns the receipt/response
    @abc.abstractmethod
    async def wait_for_receipt(self, **kwargs) -> Any:
        pass


# Proxy for a chain-specific transaction
@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class Transaction[
    ChainType: Chain,
](ABC):
    @abc.abstractmethod
    async def broadcast(self) -> SentTransaction[ChainType]:
        pass

    @property
    @abc.abstractmethod
    def chain(self) -> ChainType:
        pass


# Avoid a circular import
from . import ethereum, solana, tron  # noqa: E402
