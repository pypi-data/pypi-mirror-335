# Reference:
# https://github.com/circlefin/solana-cctp-contracts/blob/master/examples/utils.ts
# https://github.com/tristeroresearch/cache-half-full/blob/dev-solana-add-bond/backend/solutils.py

import functools
import typing
from typing import Iterable

from solders.pubkey import Pubkey


def encode_address(pubkey: Pubkey) -> bytes:
    return bytes(pubkey)


@functools.cache
def find_program_address_and_bump(
    label: str,
    program_id: Pubkey,
    extra_seeds: Iterable[str | bytes | bytearray | Pubkey] = tuple(),
) -> tuple[Pubkey, int]:
    seeds = [label.encode()]

    for seed in extra_seeds:
        match seed:
            case str():
                seeds.append(seed.encode())
            case bytes() | bytearray():
                seeds.append(seed)
            case Pubkey() | memoryview():
                seeds.append(bytes(seed))
            case _ as arg:
                typing.assert_never(arg)

    return Pubkey.find_program_address(seeds, program_id)


def find_program_address(
    label: str,
    program_id: Pubkey,
    extra_seeds: Iterable[str | bytes | bytearray | Pubkey] = tuple(),
) -> Pubkey:
    return find_program_address_and_bump(label, program_id, extra_seeds)[0]
