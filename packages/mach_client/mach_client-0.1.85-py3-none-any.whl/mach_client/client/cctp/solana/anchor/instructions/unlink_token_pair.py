from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class UnlinkTokenPairArgs(typing.TypedDict):
    params: types.unink_token_pair_params.UninkTokenPairParams


layout = borsh.CStruct(
    "params" / types.unink_token_pair_params.UninkTokenPairParams.layout
)


class UnlinkTokenPairAccounts(typing.TypedDict):
    payee: Pubkey
    token_controller: Pubkey
    token_minter: Pubkey
    token_pair: Pubkey
    event_authority: Pubkey
    program: Pubkey


def unlink_token_pair(
    args: UnlinkTokenPairArgs,
    accounts: UnlinkTokenPairAccounts,
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
        AccountMeta(pubkey=accounts["token_pair"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["event_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["program"], is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"4\xc6drh\xaeU:"
    encoded_args = layout.build(
        {
            "params": args["params"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
