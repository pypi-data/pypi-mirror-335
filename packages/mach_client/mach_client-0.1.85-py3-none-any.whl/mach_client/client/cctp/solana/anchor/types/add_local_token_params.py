from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class AddLocalTokenParamsJSON(typing.TypedDict):
    pass


@dataclass
class AddLocalTokenParams:
    layout: typing.ClassVar = borsh.CStruct()

    @classmethod
    def from_decoded(cls, obj: Container) -> "AddLocalTokenParams":
        return cls()

    def to_encodable(self) -> dict[str, typing.Any]:
        return {}

    def to_json(self) -> AddLocalTokenParamsJSON:
        return {}

    @classmethod
    def from_json(cls, obj: AddLocalTokenParamsJSON) -> "AddLocalTokenParams":
        return cls()
