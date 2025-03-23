from __future__ import annotations
import dataclasses
import typing

from solana.rpc.async_api import AsyncClient

from .. import config
from ..chain import SolanaChain
from .chain_client import ChainClient


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class SolanaClient[Chain: SolanaChain](ChainClient[Chain]):
    native: AsyncClient

    @classmethod
    @typing.override
    async def create(cls, chain: Chain) -> SolanaClient[Chain]:
        client = AsyncClient(config.config.endpoint_uris[chain])
        return cls(chain=chain, native=client)

    @typing.override
    async def close(self) -> None:
        if await self.is_connected():
            await self.native.close()

    @typing.override
    async def is_connected(self) -> bool:
        return await self.native.is_connected()

    @typing.override
    async def reconnect(self) -> None:
        await super().reconnect()
