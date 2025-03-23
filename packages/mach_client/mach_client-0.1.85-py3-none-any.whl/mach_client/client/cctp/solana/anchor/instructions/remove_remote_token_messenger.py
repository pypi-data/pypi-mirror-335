from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class RemoveRemoteTokenMessengerArgs(typing.TypedDict):
    params: types.remove_remote_token_messenger_params.RemoveRemoteTokenMessengerParams


layout = borsh.CStruct(
    "params"
    / types.remove_remote_token_messenger_params.RemoveRemoteTokenMessengerParams.layout
)


class RemoveRemoteTokenMessengerAccounts(typing.TypedDict):
    payee: Pubkey
    owner: Pubkey
    token_messenger: Pubkey
    remote_token_messenger: Pubkey
    event_authority: Pubkey
    program: Pubkey


def remove_remote_token_messenger(
    args: RemoveRemoteTokenMessengerArgs,
    accounts: RemoveRemoteTokenMessengerAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["payee"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=False),
        AccountMeta(
            pubkey=accounts["token_messenger"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["remote_token_messenger"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["event_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["program"], is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"ArBU\xa9b\xb1\x92"
    encoded_args = layout.build(
        {
            "params": args["params"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
