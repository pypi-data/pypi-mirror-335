from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class AddRemoteTokenMessengerParamsJSON(typing.TypedDict):
    domain: int
    token_messenger: str


@dataclass
class AddRemoteTokenMessengerParams:
    layout: typing.ClassVar = borsh.CStruct(
        "domain" / borsh.U32, "token_messenger" / BorshPubkey
    )
    domain: int
    token_messenger: Pubkey

    @classmethod
    def from_decoded(cls, obj: Container) -> "AddRemoteTokenMessengerParams":
        return cls(domain=obj.domain, token_messenger=obj.token_messenger)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"domain": self.domain, "token_messenger": self.token_messenger}

    def to_json(self) -> AddRemoteTokenMessengerParamsJSON:
        return {"domain": self.domain, "token_messenger": str(self.token_messenger)}

    @classmethod
    def from_json(
        cls, obj: AddRemoteTokenMessengerParamsJSON
    ) -> "AddRemoteTokenMessengerParams":
        return cls(
            domain=obj["domain"],
            token_messenger=Pubkey.from_string(obj["token_messenger"]),
        )
