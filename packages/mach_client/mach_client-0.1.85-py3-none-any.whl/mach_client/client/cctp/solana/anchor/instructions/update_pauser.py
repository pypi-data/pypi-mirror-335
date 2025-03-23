from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class UpdatePauserArgs(typing.TypedDict):
    params: types.update_pauser_params.UpdatePauserParams


layout = borsh.CStruct("params" / types.update_pauser_params.UpdatePauserParams.layout)


class UpdatePauserAccounts(typing.TypedDict):
    owner: Pubkey
    token_messenger: Pubkey
    token_minter: Pubkey
    event_authority: Pubkey
    program: Pubkey


def update_pauser(
    args: UpdatePauserArgs,
    accounts: UpdatePauserAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=False),
        AccountMeta(
            pubkey=accounts["token_messenger"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["token_minter"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["event_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["program"], is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x8c\xab\xd3\x849\xc9\x10\xfe"
    encoded_args = layout.build(
        {
            "params": args["params"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
