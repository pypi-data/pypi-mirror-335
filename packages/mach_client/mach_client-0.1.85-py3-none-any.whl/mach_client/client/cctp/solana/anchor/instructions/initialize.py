from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class InitializeArgs(typing.TypedDict):
    params: types.initialize_params.InitializeParams


layout = borsh.CStruct("params" / types.initialize_params.InitializeParams.layout)


class InitializeAccounts(typing.TypedDict):
    payer: Pubkey
    upgrade_authority: Pubkey
    authority_pda: Pubkey
    token_messenger: Pubkey
    token_minter: Pubkey
    token_messenger_minter_program_data: Pubkey
    token_messenger_minter_program: Pubkey
    event_authority: Pubkey
    program: Pubkey


def initialize(
    args: InitializeArgs,
    accounts: InitializeAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["payer"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["upgrade_authority"], is_signer=True, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["authority_pda"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_messenger"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["token_minter"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["token_messenger_minter_program_data"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["token_messenger_minter_program"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["event_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["program"], is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xaf\xafm\x1f\r\x98\x9b\xed"
    encoded_args = layout.build(
        {
            "params": args["params"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
