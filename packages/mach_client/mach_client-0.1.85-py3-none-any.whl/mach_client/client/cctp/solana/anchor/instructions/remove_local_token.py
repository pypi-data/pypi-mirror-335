from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class RemoveLocalTokenArgs(typing.TypedDict):
    params: types.remove_local_token_params.RemoveLocalTokenParams


layout = borsh.CStruct(
    "params" / types.remove_local_token_params.RemoveLocalTokenParams.layout
)


class RemoveLocalTokenAccounts(typing.TypedDict):
    payee: Pubkey
    token_controller: Pubkey
    token_minter: Pubkey
    local_token: Pubkey
    custody_token_account: Pubkey
    event_authority: Pubkey
    program: Pubkey


def remove_local_token(
    args: RemoveLocalTokenArgs,
    accounts: RemoveLocalTokenAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["payee"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["token_controller"], is_signer=True, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_minter"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["local_token"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["custody_token_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["event_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["program"], is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x1b+B\xaa\xbc,ma"
    encoded_args = layout.build(
        {
            "params": args["params"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
