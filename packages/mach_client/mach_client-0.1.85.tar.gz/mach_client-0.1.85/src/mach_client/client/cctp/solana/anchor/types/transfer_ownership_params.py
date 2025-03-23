from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class TransferOwnershipParamsJSON(typing.TypedDict):
    new_owner: str


@dataclass
class TransferOwnershipParams:
    layout: typing.ClassVar = borsh.CStruct("new_owner" / BorshPubkey)
    new_owner: Pubkey

    @classmethod
    def from_decoded(cls, obj: Container) -> "TransferOwnershipParams":
        return cls(new_owner=obj.new_owner)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"new_owner": self.new_owner}

    def to_json(self) -> TransferOwnershipParamsJSON:
        return {"new_owner": str(self.new_owner)}

    @classmethod
    def from_json(cls, obj: TransferOwnershipParamsJSON) -> "TransferOwnershipParams":
        return cls(new_owner=Pubkey.from_string(obj["new_owner"]))
