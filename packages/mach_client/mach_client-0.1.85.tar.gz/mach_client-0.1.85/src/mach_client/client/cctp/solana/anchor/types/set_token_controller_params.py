from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class SetTokenControllerParamsJSON(typing.TypedDict):
    token_controller: str


@dataclass
class SetTokenControllerParams:
    layout: typing.ClassVar = borsh.CStruct("token_controller" / BorshPubkey)
    token_controller: Pubkey

    @classmethod
    def from_decoded(cls, obj: Container) -> "SetTokenControllerParams":
        return cls(token_controller=obj.token_controller)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"token_controller": self.token_controller}

    def to_json(self) -> SetTokenControllerParamsJSON:
        return {"token_controller": str(self.token_controller)}

    @classmethod
    def from_json(cls, obj: SetTokenControllerParamsJSON) -> "SetTokenControllerParams":
        return cls(token_controller=Pubkey.from_string(obj["token_controller"]))
