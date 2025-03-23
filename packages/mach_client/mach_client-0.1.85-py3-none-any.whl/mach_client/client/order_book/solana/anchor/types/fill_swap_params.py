from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class FillSwapParamsJSON(typing.TypedDict):
    order_idx: int
    trade_match_id: int
    src_quantity: int
    dst_quantity: int


@dataclass
class FillSwapParams:
    layout: typing.ClassVar = borsh.CStruct(
        "order_idx" / borsh.U64,
        "trade_match_id" / borsh.U64,
        "src_quantity" / borsh.U64,
        "dst_quantity" / borsh.U64,
    )
    order_idx: int
    trade_match_id: int
    src_quantity: int
    dst_quantity: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "FillSwapParams":
        return cls(
            order_idx=obj.order_idx,
            trade_match_id=obj.trade_match_id,
            src_quantity=obj.src_quantity,
            dst_quantity=obj.dst_quantity,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "order_idx": self.order_idx,
            "trade_match_id": self.trade_match_id,
            "src_quantity": self.src_quantity,
            "dst_quantity": self.dst_quantity,
        }

    def to_json(self) -> FillSwapParamsJSON:
        return {
            "order_idx": self.order_idx,
            "trade_match_id": self.trade_match_id,
            "src_quantity": self.src_quantity,
            "dst_quantity": self.dst_quantity,
        }

    @classmethod
    def from_json(cls, obj: FillSwapParamsJSON) -> "FillSwapParams":
        return cls(
            order_idx=obj["order_idx"],
            trade_match_id=obj["trade_match_id"],
            src_quantity=obj["src_quantity"],
            dst_quantity=obj["dst_quantity"],
        )
