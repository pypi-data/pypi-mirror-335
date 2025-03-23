from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class DepositForBurnArgs(typing.TypedDict):
    params: types.deposit_for_burn_params.DepositForBurnParams


layout = borsh.CStruct(
    "params" / types.deposit_for_burn_params.DepositForBurnParams.layout
)


class DepositForBurnAccounts(typing.TypedDict):
    owner: Pubkey
    event_rent_payer: Pubkey
    sender_authority_pda: Pubkey
    burn_token_account: Pubkey
    message_transmitter: Pubkey
    token_messenger: Pubkey
    remote_token_messenger: Pubkey
    token_minter: Pubkey
    local_token: Pubkey
    burn_token_mint: Pubkey
    message_sent_event_data: Pubkey
    message_transmitter_program: Pubkey
    token_messenger_minter_program: Pubkey
    event_authority: Pubkey
    program: Pubkey


def deposit_for_burn(
    args: DepositForBurnArgs,
    accounts: DepositForBurnAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=False),
        AccountMeta(
            pubkey=accounts["event_rent_payer"], is_signer=True, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["sender_authority_pda"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["burn_token_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["message_transmitter"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_messenger"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["remote_token_messenger"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["token_minter"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["local_token"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["burn_token_mint"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["message_sent_event_data"], is_signer=True, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["message_transmitter_program"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["token_messenger_minter_program"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["event_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["program"], is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xd7<=.r7\x80\xb0"
    encoded_args = layout.build(
        {
            "params": args["params"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
