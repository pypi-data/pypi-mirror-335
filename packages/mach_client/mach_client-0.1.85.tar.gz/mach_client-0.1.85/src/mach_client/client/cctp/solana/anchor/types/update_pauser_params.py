from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class UpdatePauserParamsJSON(typing.TypedDict):
    new_pauser: str


@dataclass
class UpdatePauserParams:
    layout: typing.ClassVar = borsh.CStruct("new_pauser" / BorshPubkey)
    new_pauser: Pubkey

    @classmethod
    def from_decoded(cls, obj: Container) -> "UpdatePauserParams":
        return cls(new_pauser=obj.new_pauser)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"new_pauser": self.new_pauser}

    def to_json(self) -> UpdatePauserParamsJSON:
        return {"new_pauser": str(self.new_pauser)}

    @classmethod
    def from_json(cls, obj: UpdatePauserParamsJSON) -> "UpdatePauserParams":
        return cls(new_pauser=Pubkey.from_string(obj["new_pauser"]))
