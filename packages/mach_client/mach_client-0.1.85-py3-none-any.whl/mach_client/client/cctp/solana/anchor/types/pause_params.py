from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class PauseParamsJSON(typing.TypedDict):
    pass


@dataclass
class PauseParams:
    layout: typing.ClassVar = borsh.CStruct()

    @classmethod
    def from_decoded(cls, obj: Container) -> "PauseParams":
        return cls()

    def to_encodable(self) -> dict[str, typing.Any]:
        return {}

    def to_json(self) -> PauseParamsJSON:
        return {}

    @classmethod
    def from_json(cls, obj: PauseParamsJSON) -> "PauseParams":
        return cls()
