from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class SetMaxBurnAmountPerMessageArgs(typing.TypedDict):
    params: types.set_max_burn_amount_per_message_params.SetMaxBurnAmountPerMessageParams


layout = borsh.CStruct(
    "params"
    / types.set_max_burn_amount_per_message_params.SetMaxBurnAmountPerMessageParams.layout
)


class SetMaxBurnAmountPerMessageAccounts(typing.TypedDict):
    token_controller: Pubkey
    token_minter: Pubkey
    local_token: Pubkey
    event_authority: Pubkey
    program: Pubkey


def set_max_burn_amount_per_message(
    args: SetMaxBurnAmountPerMessageArgs,
    accounts: SetMaxBurnAmountPerMessageAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["token_controller"], is_signer=True, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_minter"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["local_token"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["event_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["program"], is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x1e\x80\x91\xf0F\xedm\xcf"
    encoded_args = layout.build(
        {
            "params": args["params"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
