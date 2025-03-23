from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class LinkTokenPairParamsJSON(typing.TypedDict):
    local_token: str
    remote_domain: int
    remote_token: str


@dataclass
class LinkTokenPairParams:
    layout: typing.ClassVar = borsh.CStruct(
        "local_token" / BorshPubkey,
        "remote_domain" / borsh.U32,
        "remote_token" / BorshPubkey,
    )
    local_token: Pubkey
    remote_domain: int
    remote_token: Pubkey

    @classmethod
    def from_decoded(cls, obj: Container) -> "LinkTokenPairParams":
        return cls(
            local_token=obj.local_token,
            remote_domain=obj.remote_domain,
            remote_token=obj.remote_token,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "local_token": self.local_token,
            "remote_domain": self.remote_domain,
            "remote_token": self.remote_token,
        }

    def to_json(self) -> LinkTokenPairParamsJSON:
        return {
            "local_token": str(self.local_token),
            "remote_domain": self.remote_domain,
            "remote_token": str(self.remote_token),
        }

    @classmethod
    def from_json(cls, obj: LinkTokenPairParamsJSON) -> "LinkTokenPairParams":
        return cls(
            local_token=Pubkey.from_string(obj["local_token"]),
            remote_domain=obj["remote_domain"],
            remote_token=Pubkey.from_string(obj["remote_token"]),
        )
