from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class RemoveLocalTokenParamsJSON(typing.TypedDict):
    pass


@dataclass
class RemoveLocalTokenParams:
    layout: typing.ClassVar = borsh.CStruct()

    @classmethod
    def from_decoded(cls, obj: Container) -> "RemoveLocalTokenParams":
        return cls()

    def to_encodable(self) -> dict[str, typing.Any]:
        return {}

    def to_json(self) -> RemoveLocalTokenParamsJSON:
        return {}

    @classmethod
    def from_json(cls, obj: RemoveLocalTokenParamsJSON) -> "RemoveLocalTokenParams":
        return cls()
