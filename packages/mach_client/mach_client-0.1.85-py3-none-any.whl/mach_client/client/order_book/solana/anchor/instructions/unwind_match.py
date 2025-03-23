from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class UnwindMatchAccounts(typing.TypedDict):
    authority: Pubkey
    oapp: Pubkey
    order: Pubkey
    trade_match: Pubkey
    staking_account: Pubkey
    staking_bond_account: Pubkey
    user_token_account: Pubkey
    bonder_bond_token_account: Pubkey


def unwind_match(
    accounts: UnwindMatchAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["authority"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["oapp"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["order"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["trade_match"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["staking_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["staking_bond_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["user_token_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["bonder_bond_token_account"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xc6\x8cu\xf8\xe7qC\xe8"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
