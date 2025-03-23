# Reference:
# https://github.com/tristeroresearch/dapp/blob/dev/src/chains/solana/depositForBurn.ts

from __future__ import annotations
import typing

from solders.keypair import Keypair
from solders.pubkey import Pubkey

from ....account import SolanaAccount, SolanaAccountID
from ....asset import SolanaToken
from ....chain import SolanaChain
from ....chain_client import SolanaClient
from ....transaction import SolanaTransaction
from ...types import OrderData
from ....utility import solana as solana_utility
from .anchor import instructions
from .anchor.instructions import (
    DepositForBurnAccounts,
    DepositForBurnArgs,
)
from .anchor.types import DepositForBurnParams

if typing.TYPE_CHECKING:
    from ....client import MachClient


async def create_cctp_burn_transaction[SrcChainType: SolanaChain](
    *,
    client: MachClient,
    src_client: SolanaClient[SrcChainType],
    src_token: SolanaToken[SrcChainType],
    destination_domain: int,
    token_messenger_minter_address: str,
    order_data: OrderData,
    account: SolanaAccount[SrcChainType],
    recipient: bytes,
) -> SolanaTransaction[SrcChainType]:
    mint_recipient = Pubkey(recipient)

    params = DepositForBurnParams(
        amount=order_data.order_funding.src_amount_in,
        destination_domain=destination_domain,
        mint_recipient=mint_recipient,
    )

    args = DepositForBurnArgs(params=params)

    owner = typing.cast(SolanaAccountID, account).pubkey
    burn_token_account = typing.cast(SolanaToken, src_token).associated_token_account(
        owner
    )

    message_transmitter = Pubkey.from_string(
        client.cctp_message_transmitter_address(src_client.chain)
    )
    token_messenger_minter = Pubkey.from_string(token_messenger_minter_address)

    usdc_mint = typing.cast(SolanaToken, src_token).mint

    accounts = DepositForBurnAccounts(
        owner=owner,
        event_rent_payer=owner,
        sender_authority_pda=solana_utility.find_program_address(
            "sender_authority", token_messenger_minter
        ),
        burn_token_account=burn_token_account,
        message_transmitter=solana_utility.find_program_address(
            "message_transmitter", message_transmitter
        ),
        token_messenger=solana_utility.find_program_address(
            "token_messenger", token_messenger_minter
        ),
        remote_token_messenger=solana_utility.find_program_address(
            "remote_token_messenger",
            token_messenger_minter,
            (str(destination_domain),),
        ),
        token_minter=solana_utility.find_program_address(
            "token_minter", token_messenger_minter
        ),
        local_token=solana_utility.find_program_address(
            "local_token",
            token_messenger_minter,
            (usdc_mint,),
        ),
        burn_token_mint=usdc_mint,
        message_sent_event_data=Keypair().pubkey(),
        message_transmitter_program=message_transmitter,
        token_messenger_minter_program=token_messenger_minter,
        event_authority=solana_utility.find_program_address(
            "__event_authority", token_messenger_minter
        ),
        program=token_messenger_minter,
    )

    instruction = instructions.deposit_for_burn(args=args, accounts=accounts)

    return await SolanaTransaction.create(
        src_client, (instruction,), (typing.cast(SolanaAccount, account),)
    )
