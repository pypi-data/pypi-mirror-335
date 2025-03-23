from __future__ import annotations
import asyncio
import dataclasses
import pprint
import typing
from typing import ClassVar

from eth_account.datastructures import SignedTransaction
from hexbytes import HexBytes
from web3 import AsyncWeb3
from web3._utils import async_transactions
from web3.contract.async_contract import AsyncContractFunction
from web3.types import TxParams, TxReceipt

from ..account import EthereumAccount
from ..chain import EthereumChain
from ..chain_client import EthereumClient
from .transaction import SentTransaction, Transaction


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class EthereumSentTransaction[Chain: EthereumChain](SentTransaction[Chain]):
    client: EthereumClient[Chain]
    transaction_hash: HexBytes

    @property
    @typing.override
    def id(self) -> str:
        return self.transaction_hash.to_0x_hex()

    @property
    @typing.override
    def chain(self) -> Chain:
        return self.client.chain

    @typing.override
    async def wait_for_receipt(self, **kwargs) -> TxReceipt:
        receipt = await self.client.w3.eth.wait_for_transaction_receipt(
            self.transaction_hash, **kwargs
        )
        assert (
            receipt["status"] == 0x1
        ), f"Transaction failed:\n{pprint.pformat(receipt)}"
        return receipt


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class EthereumTransaction[Chain: EthereumChain](Transaction[Chain]):
    DEFAULT_GAS_MULTIPLIER: ClassVar[float] = 1.5

    client: EthereumClient[Chain]
    transaction: SignedTransaction

    @staticmethod
    async def fill_transaction_defaults(
        w3: AsyncWeb3,
        params: TxParams = TxParams(),
    ) -> TxParams:
        return await async_transactions.async_fill_transaction_defaults(w3, params)

    @classmethod
    async def from_transaction_params(
        cls,
        client: EthereumClient[Chain],
        params: TxParams,
        signer: EthereumAccount[Chain],
        gas_multiplier: float = DEFAULT_GAS_MULTIPLIER,
    ) -> EthereumTransaction[Chain]:
        params, nonce = await asyncio.gather(
            async_transactions.async_fill_transaction_defaults(client.w3, params),
            client.w3.eth.get_transaction_count(signer.native.address, "latest"),
        )

        params.update(
            # Ensures the transaction goes through
            gas=int(gas_multiplier * params["gas"]),  # type: ignore
            # This isn't filled in by `async_fill_transaction_defaults`
            nonce=nonce,
        )

        signed_transaction = signer.native.sign_transaction(params)  # type: ignore

        return cls(client=client, transaction=signed_transaction)

    @classmethod
    async def from_contract_function(
        cls,
        client: EthereumClient[Chain],
        contract_function: AsyncContractFunction,
        signer: EthereumAccount,
        gas_multiplier: float = DEFAULT_GAS_MULTIPLIER,
    ) -> EthereumTransaction[Chain]:
        params, nonce = await asyncio.gather(
            contract_function.build_transaction({"from": signer.native.address}),
            client.w3.eth.get_transaction_count(signer.native.address, "latest"),
        )

        params.update(
            # Ensures the transaction goes through
            gas=int(gas_multiplier * params["gas"]),  # type: ignore
            # This isn't filled in by `build_transaction`
            nonce=nonce,
        )

        signed_transaction = signer.native.sign_transaction(params)  # type: ignore

        return cls(client=client, transaction=signed_transaction)

    @typing.override
    async def broadcast(self) -> EthereumSentTransaction[Chain]:
        transaction_hash = await self.client.w3.eth.send_raw_transaction(
            self.transaction.raw_transaction
        )
        return EthereumSentTransaction(
            client=self.client, transaction_hash=transaction_hash
        )

    @property
    @typing.override
    def chain(self) -> Chain:
        return self.client.chain
