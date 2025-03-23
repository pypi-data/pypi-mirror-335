from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class LinkTokenPairArgs(typing.TypedDict):
    params: types.link_token_pair_params.LinkTokenPairParams


layout = borsh.CStruct(
    "params" / types.link_token_pair_params.LinkTokenPairParams.layout
)


class LinkTokenPairAccounts(typing.TypedDict):
    payer: Pubkey
    token_controller: Pubkey
    token_minter: Pubkey
    token_pair: Pubkey
    event_authority: Pubkey
    program: Pubkey


def link_token_pair(
    args: LinkTokenPairArgs,
    accounts: LinkTokenPairAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["payer"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["token_controller"], is_signer=True, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_minter"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["token_pair"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["event_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["program"], is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"D\xa2\x18h}.\x82\x0c"
    encoded_args = layout.build(
        {
            "params": args["params"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
