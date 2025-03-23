from __future__ import annotations
import typing

from ...account import (
    Account,
    AccountID,
    EthereumAccount,
    SolanaAccount,
    SolanaAccountID,
)
from ...asset import SolanaToken, Token
from ...chain import Chain
from ...chain_client import (
    ChainClient,
    EthereumClient,
    SolanaClient,
)
from ...transaction import Transaction
from ..types import OrderData
from . import ethereum, solana

if typing.TYPE_CHECKING:
    from ...client import MachClient


async def create_cctp_burn_transaction[SrcChainType: Chain, DestChainType: Chain](
    *,
    client: MachClient,
    src_client: ChainClient[SrcChainType],
    src_token: Token[SrcChainType],
    dest_token: Token[DestChainType],
    order_data: OrderData,
    account: Account[SrcChainType],
    recipient: AccountID[DestChainType],
) -> Transaction[SrcChainType]:
    token_messenger_minter_address = client.cctp_token_messenger_minter_address(
        src_client.chain
    )
    destination_domain = recipient.chain.cctp_domain

    # See the [Mint recipient for Solana as Destination Chain section](https://developers.circle.com/stablecoins/solana-programs)
    if isinstance(recipient, SolanaAccountID):
        recipient_token_account = typing.cast(
            SolanaToken, dest_token
        ).associated_token_account(recipient.pubkey)
        recipient_bytes = bytes(recipient_token_account)
    else:
        recipient_bytes = recipient.encode_address()

    recipient_bytes = recipient_bytes.rjust(32, b"\0")

    match src_client:
        case EthereumClient():
            return await ethereum.create_cctp_burn_transaction(
                src_client=src_client,
                destination_domain=destination_domain,
                token_messenger_minter_address=token_messenger_minter_address,
                order_data=order_data,
                account=typing.cast(EthereumAccount, account),
                recipient=recipient_bytes,
            )

        case SolanaClient():
            return await solana.create_cctp_burn_transaction(
                client=client,
                src_client=src_client,
                src_token=typing.cast(SolanaToken, src_token),
                destination_domain=destination_domain,
                token_messenger_minter_address=token_messenger_minter_address,
                order_data=order_data,
                account=typing.cast(SolanaAccount, account),
                recipient=recipient_bytes,
            )

        case _:
            raise NotImplementedError(src_client.chain)


__all__ = ["create_cctp_burn_transaction"]
