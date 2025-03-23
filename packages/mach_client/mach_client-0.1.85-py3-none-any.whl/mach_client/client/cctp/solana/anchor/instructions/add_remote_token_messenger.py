from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class AddRemoteTokenMessengerArgs(typing.TypedDict):
    params: types.add_remote_token_messenger_params.AddRemoteTokenMessengerParams


layout = borsh.CStruct(
    "params"
    / types.add_remote_token_messenger_params.AddRemoteTokenMessengerParams.layout
)


class AddRemoteTokenMessengerAccounts(typing.TypedDict):
    payer: Pubkey
    owner: Pubkey
    token_messenger: Pubkey
    remote_token_messenger: Pubkey
    event_authority: Pubkey
    program: Pubkey


def add_remote_token_messenger(
    args: AddRemoteTokenMessengerArgs,
    accounts: AddRemoteTokenMessengerAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["payer"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=False),
        AccountMeta(
            pubkey=accounts["token_messenger"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["remote_token_messenger"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["event_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["program"], is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x0c\x95\xac\xa5o\xca\x18!"
    encoded_args = layout.build(
        {
            "params": args["params"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
