from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class CreateMatchParamsJSON(typing.TypedDict):
    order_idx: int
    src_quantity: int
    dst_quantity: int


@dataclass
class CreateMatchParams:
    layout: typing.ClassVar = borsh.CStruct(
        "order_idx" / borsh.U64, "src_quantity" / borsh.U64, "dst_quantity" / borsh.U64
    )
    order_idx: int
    src_quantity: int
    dst_quantity: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "CreateMatchParams":
        return cls(
            order_idx=obj.order_idx,
            src_quantity=obj.src_quantity,
            dst_quantity=obj.dst_quantity,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "order_idx": self.order_idx,
            "src_quantity": self.src_quantity,
            "dst_quantity": self.dst_quantity,
        }

    def to_json(self) -> CreateMatchParamsJSON:
        return {
            "order_idx": self.order_idx,
            "src_quantity": self.src_quantity,
            "dst_quantity": self.dst_quantity,
        }

    @classmethod
    def from_json(cls, obj: CreateMatchParamsJSON) -> "CreateMatchParams":
        return cls(
            order_idx=obj["order_idx"],
            src_quantity=obj["src_quantity"],
            dst_quantity=obj["dst_quantity"],
        )
