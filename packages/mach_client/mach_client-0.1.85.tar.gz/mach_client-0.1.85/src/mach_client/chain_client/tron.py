from __future__ import annotations
import dataclasses
import typing

from tronpy.async_tron import AsyncTron
from tronpy.providers import AsyncHTTPProvider

from .. import config
from ..chain import TronChain
from .chain_client import ChainClient


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class TronClient[Chain: TronChain](ChainClient[Chain]):
    native: AsyncTron

    @classmethod
    @typing.override
    async def create(cls, chain: Chain) -> TronClient[Chain]:
        provider = AsyncHTTPProvider(config.config.endpoint_uris[chain], timeout=60.0)
        client = AsyncTron(provider)
        return cls(chain=chain, native=client)

    @typing.override
    async def close(self) -> None:
        if await self.is_connected():
            await self.native.close()

    @typing.override
    async def is_connected(self) -> bool:
        # TODO: is_closed tells us if the connection is closed, but we should also check if the connection is open
        # However, the state enum that tells us if the connection is open is not exposed by the library
        return not self.native.provider.client.is_closed

    @typing.override
    async def reconnect(self) -> None:
        await super().reconnect()