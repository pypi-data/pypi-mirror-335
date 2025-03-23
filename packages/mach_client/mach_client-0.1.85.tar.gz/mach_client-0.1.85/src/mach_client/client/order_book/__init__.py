from __future__ import annotations
import typing

from eth_typing import ChecksumAddress

from ...account import (
    Account,
    EthereumAccount,
    SolanaAccount,
    TronAccount,
)
from ...asset import SolanaToken, Token
from ...chain import Chain
from ...chain_client import (
    ChainClient,
    EthereumClient,
    SolanaClient,
    TronClient,
)
from ...transaction import Transaction
from ..types import OrderData
from . import ethereum, solana, tron


async def create_place_order_transaction[SrcChainType: Chain, DestChainType: Chain](
    *,
    src_client: ChainClient[SrcChainType],
    src_token: Token[SrcChainType],
    order_data: OrderData,
    account: Account[SrcChainType],
) -> Transaction[SrcChainType]:
    order_book_address = order_data.contract_address

    match src_client:
        case EthereumClient():
            return await ethereum.create_place_order_transaction(
                src_client=src_client,
                order_book_address=typing.cast(ChecksumAddress, order_book_address),
                order_data=order_data,
                account=typing.cast(EthereumAccount, account),
            )

        case SolanaClient():
            return await solana.create_place_order_transaction(
                src_client=src_client,
                src_token=typing.cast(SolanaToken, src_token),
                order_book_address=order_book_address,
                order_data=order_data,
                account=typing.cast(SolanaAccount, account),
            )

        case TronClient():
            return await tron.create_place_order_transaction(
                src_client=src_client,
                order_book_address=order_book_address,
                order_data=order_data,
                account=typing.cast(TronAccount, account),
            )

        case _:
            raise NotImplementedError(src_client.chain)


__all__ = ["create_place_order_transaction"]
