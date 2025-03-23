from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class PlaceOrderParamsJSON(typing.TypedDict):
    source_sell_amount: int
    min_sell_amount: int
    dst_token_mint: list[int]
    dst_buy_amount: int
    eid: int
    target_address: list[int]
    bond_asset_mint: str
    bond_amount: int
    bond_fee: int


@dataclass
class PlaceOrderParams:
    layout: typing.ClassVar = borsh.CStruct(
        "source_sell_amount" / borsh.U64,
        "min_sell_amount" / borsh.U64,
        "dst_token_mint" / borsh.U8[32],
        "dst_buy_amount" / borsh.U64,
        "eid" / borsh.U32,
        "target_address" / borsh.U8[32],
        "bond_asset_mint" / BorshPubkey,
        "bond_amount" / borsh.U64,
        "bond_fee" / borsh.U16,
    )
    source_sell_amount: int
    min_sell_amount: int
    dst_token_mint: list[int]
    dst_buy_amount: int
    eid: int
    target_address: list[int]
    bond_asset_mint: Pubkey
    bond_amount: int
    bond_fee: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "PlaceOrderParams":
        return cls(
            source_sell_amount=obj.source_sell_amount,
            min_sell_amount=obj.min_sell_amount,
            dst_token_mint=obj.dst_token_mint,
            dst_buy_amount=obj.dst_buy_amount,
            eid=obj.eid,
            target_address=obj.target_address,
            bond_asset_mint=obj.bond_asset_mint,
            bond_amount=obj.bond_amount,
            bond_fee=obj.bond_fee,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "source_sell_amount": self.source_sell_amount,
            "min_sell_amount": self.min_sell_amount,
            "dst_token_mint": self.dst_token_mint,
            "dst_buy_amount": self.dst_buy_amount,
            "eid": self.eid,
            "target_address": self.target_address,
            "bond_asset_mint": self.bond_asset_mint,
            "bond_amount": self.bond_amount,
            "bond_fee": self.bond_fee,
        }

    def to_json(self) -> PlaceOrderParamsJSON:
        return {
            "source_sell_amount": self.source_sell_amount,
            "min_sell_amount": self.min_sell_amount,
            "dst_token_mint": self.dst_token_mint,
            "dst_buy_amount": self.dst_buy_amount,
            "eid": self.eid,
            "target_address": self.target_address,
            "bond_asset_mint": str(self.bond_asset_mint),
            "bond_amount": self.bond_amount,
            "bond_fee": self.bond_fee,
        }

    @classmethod
    def from_json(cls, obj: PlaceOrderParamsJSON) -> "PlaceOrderParams":
        return cls(
            source_sell_amount=obj["source_sell_amount"],
            min_sell_amount=obj["min_sell_amount"],
            dst_token_mint=obj["dst_token_mint"],
            dst_buy_amount=obj["dst_buy_amount"],
            eid=obj["eid"],
            target_address=obj["target_address"],
            bond_asset_mint=Pubkey.from_string(obj["bond_asset_mint"]),
            bond_amount=obj["bond_amount"],
            bond_fee=obj["bond_fee"],
        )
