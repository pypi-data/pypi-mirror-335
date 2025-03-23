from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class RemoveRemoteTokenMessengerParamsJSON(typing.TypedDict):
    pass


@dataclass
class RemoveRemoteTokenMessengerParams:
    layout: typing.ClassVar = borsh.CStruct()

    @classmethod
    def from_decoded(cls, obj: Container) -> "RemoveRemoteTokenMessengerParams":
        return cls()

    def to_encodable(self) -> dict[str, typing.Any]:
        return {}

    def to_json(self) -> RemoveRemoteTokenMessengerParamsJSON:
        return {}

    @classmethod
    def from_json(
        cls, obj: RemoveRemoteTokenMessengerParamsJSON
    ) -> "RemoveRemoteTokenMessengerParams":
        return cls()
