from __future__ import annotations
import dataclasses
import typing

from solders.keypair import Keypair
from solders.pubkey import Pubkey

from ..chain import SolanaChain
from ..utility import solana
from .account import Account, AccountID


@dataclasses.dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class SolanaAccountID[Chain: SolanaChain](AccountID[Chain]):
    pubkey: Pubkey

    @classmethod
    def from_pubkey(cls, chain: Chain, pubkey: str) -> SolanaAccountID[Chain]:
        return cls(chain=chain, pubkey=Pubkey.from_string(pubkey))

    @property
    @typing.override
    def address(self) -> str:
        return str(self.pubkey)

    @typing.override
    def encode_address(self) -> bytes:
        return solana.encode_address(self.pubkey)


@dataclasses.dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class SolanaAccount[Chain: SolanaChain](Account[Chain]):
    keypair: Keypair

    @classmethod
    def from_private_key(cls, chain: Chain, private_key: str) -> SolanaAccount[Chain]:
        return cls(chain=chain, keypair=Keypair.from_base58_string(private_key))

    @property
    @typing.override
    def address(self) -> str:
        return str(self.keypair.pubkey())

    @property
    @typing.override
    def private_key(self) -> str:
        return str(self.keypair)

    @typing.override
    def encode_address(self) -> bytes:
        return solana.encode_address(self.keypair.pubkey())

    @typing.override
    def downcast(self) -> SolanaAccountID:
        return SolanaAccountID(chain=self.chain, pubkey=self.keypair.pubkey())
