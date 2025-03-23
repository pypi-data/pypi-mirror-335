from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class SetMaxBurnAmountPerMessageParamsJSON(typing.TypedDict):
    burn_limit_per_message: int


@dataclass
class SetMaxBurnAmountPerMessageParams:
    layout: typing.ClassVar = borsh.CStruct("burn_limit_per_message" / borsh.U64)
    burn_limit_per_message: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "SetMaxBurnAmountPerMessageParams":
        return cls(burn_limit_per_message=obj.burn_limit_per_message)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"burn_limit_per_message": self.burn_limit_per_message}

    def to_json(self) -> SetMaxBurnAmountPerMessageParamsJSON:
        return {"burn_limit_per_message": self.burn_limit_per_message}

    @classmethod
    def from_json(
        cls, obj: SetMaxBurnAmountPerMessageParamsJSON
    ) -> "SetMaxBurnAmountPerMessageParams":
        return cls(burn_limit_per_message=obj["burn_limit_per_message"])
