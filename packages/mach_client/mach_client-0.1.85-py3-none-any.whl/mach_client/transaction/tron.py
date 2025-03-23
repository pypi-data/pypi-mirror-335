from __future__ import annotations
import asyncio
import dataclasses
import typing
from typing import Any

from tronpy.async_tron import (
    AsyncTransaction,
    AsyncTransactionRet,
    AsyncTransactionBuilder,
    AsyncTron,
)
from tronpy.async_contract import AsyncContractMethod
import trontxsize

from ..account import TronAccount
from ..chain import TronChain
from ..chain_client import TronClient
from .transaction import SentTransaction, Transaction


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class TronSentTransaction[Chain: TronChain](SentTransaction[Chain]):
    chain_: Chain
    native: AsyncTransactionRet

    @property
    @typing.override
    def id(self) -> str:
        return self.native.txid

    @property
    @typing.override
    def chain(self) -> Chain:
        return self.chain_

    @typing.override
    async def wait_for_receipt(self, **kwargs: Any) -> dict:
        return await self.native.wait(**kwargs)


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class TronTransaction[Chain: TronChain](Transaction[Chain]):
    chain_: Chain
    native: AsyncTransaction

    @staticmethod
    async def _estimate_energy(
        client: AsyncTron,
        owner: TronAccount[Chain],
        contract_method: AsyncContractMethod,
        *args: Any,
        **kwargs: Any,
    ) -> int:
        assert (contract_address := contract_method._contract.contract_address)

        return await client.get_estimated_energy(
            owner_address=owner.address,
            contract_address=contract_address,
            function_selector=contract_method.function_signature,
            parameter=contract_method._prepare_parameter(*args, **kwargs),
        )

    @staticmethod
    def _extract_price_from_response(response: dict) -> int:
        prices = response.get("prices", "").split(",")
        recent_price: str = prices[-1]
        _timestamp, price = recent_price.split(":")

        return int(price)

    @classmethod
    async def _get_energy_price(cls, client: AsyncTron) -> int:
        response = await client.provider.make_request("wallet/getenergyprices")
        return cls._extract_price_from_response(response)

    @classmethod
    async def _get_bandwidth_price(cls, client: AsyncTron) -> int:
        response = await client.provider.make_request("wallet/getbandwidthprices")
        return cls._extract_price_from_response(response)

    @classmethod
    async def from_builder(
        cls,
        client: TronClient[Chain],
        builder: AsyncTransactionBuilder,
        signer: TronAccount[Chain],
        energy_limit: int,
    ) -> TronTransaction[Chain]:
        transaction: AsyncTransaction = await builder.with_owner(signer.address).build()
        transaction = transaction.sign(signer.private_key_)

        bandwidth_estimate = trontxsize.get_tx_size(transaction.to_json())
        bandwidth_price = await cls._get_bandwidth_price(client.native)

        # Warning: We're overwriting the default fee limit set by the client config
        builder = builder.fee_limit(energy_limit + bandwidth_estimate * bandwidth_price)

        transaction = await builder.build()
        transaction = transaction.sign(signer.private_key_)

        return cls(chain_=client.chain, native=transaction)

    @classmethod
    async def from_contract_method(
        cls,
        client: TronClient[Chain],
        signer: TronAccount[Chain],
        contract_method: AsyncContractMethod,
        *args: Any,
        **kwargs: Any,
    ) -> TronTransaction[Chain]:
        builder: AsyncTransactionBuilder = await contract_method(*args, **kwargs)
        transaction: AsyncTransaction = await builder.with_owner(signer.address).build()
        transaction = transaction.sign(signer.private_key_)

        energy_estimate, energy_price = await asyncio.gather(
            cls._estimate_energy(
                client.native, signer, contract_method, *args, **kwargs
            ),
            cls._get_energy_price(client.native),
        )

        return await cls.from_builder(
            client, builder, signer, energy_estimate * energy_price
        )

    @typing.override
    async def broadcast(self) -> TronSentTransaction[Chain]:
        broadcasted = await self.native.broadcast()
        return TronSentTransaction(chain_=self.chain, native=broadcasted)

    @property
    @typing.override
    def chain(self) -> Chain:
        return self.chain_
