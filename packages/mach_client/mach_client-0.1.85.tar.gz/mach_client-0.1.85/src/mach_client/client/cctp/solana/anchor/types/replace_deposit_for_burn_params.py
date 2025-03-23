from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class ReplaceDepositForBurnParamsJSON(typing.TypedDict):
    original_message: list[int]
    original_attestation: list[int]
    new_destination_caller: str
    new_mint_recipient: str


@dataclass
class ReplaceDepositForBurnParams:
    layout: typing.ClassVar = borsh.CStruct(
        "original_message" / borsh.Bytes,
        "original_attestation" / borsh.Bytes,
        "new_destination_caller" / BorshPubkey,
        "new_mint_recipient" / BorshPubkey,
    )
    original_message: bytes
    original_attestation: bytes
    new_destination_caller: Pubkey
    new_mint_recipient: Pubkey

    @classmethod
    def from_decoded(cls, obj: Container) -> "ReplaceDepositForBurnParams":
        return cls(
            original_message=obj.original_message,
            original_attestation=obj.original_attestation,
            new_destination_caller=obj.new_destination_caller,
            new_mint_recipient=obj.new_mint_recipient,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "original_message": self.original_message,
            "original_attestation": self.original_attestation,
            "new_destination_caller": self.new_destination_caller,
            "new_mint_recipient": self.new_mint_recipient,
        }

    def to_json(self) -> ReplaceDepositForBurnParamsJSON:
        return {
            "original_message": list(self.original_message),
            "original_attestation": list(self.original_attestation),
            "new_destination_caller": str(self.new_destination_caller),
            "new_mint_recipient": str(self.new_mint_recipient),
        }

    @classmethod
    def from_json(
        cls, obj: ReplaceDepositForBurnParamsJSON
    ) -> "ReplaceDepositForBurnParams":
        return cls(
            original_message=bytes(obj["original_message"]),
            original_attestation=bytes(obj["original_attestation"]),
            new_destination_caller=Pubkey.from_string(obj["new_destination_caller"]),
            new_mint_recipient=Pubkey.from_string(obj["new_mint_recipient"]),
        )
