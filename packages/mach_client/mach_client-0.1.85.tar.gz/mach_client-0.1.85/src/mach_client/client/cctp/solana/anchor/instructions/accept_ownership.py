from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class AcceptOwnershipArgs(typing.TypedDict):
    params: types.accept_ownership_params.AcceptOwnershipParams


layout = borsh.CStruct(
    "params" / types.accept_ownership_params.AcceptOwnershipParams.layout
)


class AcceptOwnershipAccounts(typing.TypedDict):
    pending_owner: Pubkey
    token_messenger: Pubkey
    event_authority: Pubkey
    program: Pubkey


def accept_ownership(
    args: AcceptOwnershipArgs,
    accounts: AcceptOwnershipAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["pending_owner"], is_signer=True, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_messenger"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["event_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["program"], is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xac\x17+\r\xee\xd5U\x96"
    encoded_args = layout.build(
        {
            "params": args["params"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
