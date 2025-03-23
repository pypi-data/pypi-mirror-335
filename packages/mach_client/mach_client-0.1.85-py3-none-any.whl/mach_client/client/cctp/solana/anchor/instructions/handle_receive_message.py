from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class HandleReceiveMessageArgs(typing.TypedDict):
    params: types.handle_receive_message_params.HandleReceiveMessageParams


layout = borsh.CStruct(
    "params" / types.handle_receive_message_params.HandleReceiveMessageParams.layout
)


class HandleReceiveMessageAccounts(typing.TypedDict):
    authority_pda: Pubkey
    token_messenger: Pubkey
    remote_token_messenger: Pubkey
    token_minter: Pubkey
    local_token: Pubkey
    token_pair: Pubkey
    recipient_token_account: Pubkey
    custody_token_account: Pubkey
    event_authority: Pubkey
    program: Pubkey


def handle_receive_message(
    args: HandleReceiveMessageArgs,
    accounts: HandleReceiveMessageAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["authority_pda"], is_signer=True, is_writable=False
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
        AccountMeta(pubkey=accounts["token_pair"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["recipient_token_account"],
            is_signer=False,
            is_writable=True,
        ),
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
    identifier = b"\x85f\x01\xb4\x91\x0b\x8a\xb4"
    encoded_args = layout.build(
        {
            "params": args["params"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
