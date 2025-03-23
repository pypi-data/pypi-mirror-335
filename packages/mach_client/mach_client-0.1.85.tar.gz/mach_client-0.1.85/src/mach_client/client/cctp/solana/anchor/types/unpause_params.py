from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class UnpauseParamsJSON(typing.TypedDict):
    pass


@dataclass
class UnpauseParams:
    layout: typing.ClassVar = borsh.CStruct()

    @classmethod
    def from_decoded(cls, obj: Container) -> "UnpauseParams":
        return cls()

    def to_encodable(self) -> dict[str, typing.Any]:
        return {}

    def to_json(self) -> UnpauseParamsJSON:
        return {}

    @classmethod
    def from_json(cls, obj: UnpauseParamsJSON) -> "UnpauseParams":
        return cls()
