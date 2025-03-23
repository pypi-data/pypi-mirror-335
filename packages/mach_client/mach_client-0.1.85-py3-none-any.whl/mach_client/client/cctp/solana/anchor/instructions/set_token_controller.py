from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class SetTokenControllerArgs(typing.TypedDict):
    params: types.set_token_controller_params.SetTokenControllerParams


layout = borsh.CStruct(
    "params" / types.set_token_controller_params.SetTokenControllerParams.layout
)


class SetTokenControllerAccounts(typing.TypedDict):
    owner: Pubkey
    token_messenger: Pubkey
    token_minter: Pubkey
    event_authority: Pubkey
    program: Pubkey


def set_token_controller(
    args: SetTokenControllerArgs,
    accounts: SetTokenControllerAccounts,
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
    identifier = b"X\x06b\nO;\x0f\x18"
    encoded_args = layout.build(
        {
            "params": args["params"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
