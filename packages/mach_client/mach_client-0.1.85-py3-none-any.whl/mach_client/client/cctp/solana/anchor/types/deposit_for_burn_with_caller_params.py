from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class DepositForBurnWithCallerParamsJSON(typing.TypedDict):
    amount: int
    destination_domain: int
    mint_recipient: str
    destination_caller: str


@dataclass
class DepositForBurnWithCallerParams:
    layout: typing.ClassVar = borsh.CStruct(
        "amount" / borsh.U64,
        "destination_domain" / borsh.U32,
        "mint_recipient" / BorshPubkey,
        "destination_caller" / BorshPubkey,
    )
    amount: int
    destination_domain: int
    mint_recipient: Pubkey
    destination_caller: Pubkey

    @classmethod
    def from_decoded(cls, obj: Container) -> "DepositForBurnWithCallerParams":
        return cls(
            amount=obj.amount,
            destination_domain=obj.destination_domain,
            mint_recipient=obj.mint_recipient,
            destination_caller=obj.destination_caller,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "amount": self.amount,
            "destination_domain": self.destination_domain,
            "mint_recipient": self.mint_recipient,
            "destination_caller": self.destination_caller,
        }

    def to_json(self) -> DepositForBurnWithCallerParamsJSON:
        return {
            "amount": self.amount,
            "destination_domain": self.destination_domain,
            "mint_recipient": str(self.mint_recipient),
            "destination_caller": str(self.destination_caller),
        }

    @classmethod
    def from_json(
        cls, obj: DepositForBurnWithCallerParamsJSON
    ) -> "DepositForBurnWithCallerParams":
        return cls(
            amount=obj["amount"],
            destination_domain=obj["destination_domain"],
            mint_recipient=Pubkey.from_string(obj["mint_recipient"]),
            destination_caller=Pubkey.from_string(obj["destination_caller"]),
        )
