from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class CancelOrderAccounts(typing.TypedDict):
    authority: Pubkey
    oapp: Pubkey
    admin_panel: Pubkey
    order: Pubkey


def cancel_order(
    accounts: CancelOrderAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["authority"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["oapp"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["admin_panel"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["order"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"_\x81\xed\xf0\x081\xdf\x84"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
