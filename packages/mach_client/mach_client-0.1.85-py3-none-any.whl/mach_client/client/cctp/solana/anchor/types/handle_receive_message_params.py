from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class HandleReceiveMessageParamsJSON(typing.TypedDict):
    remote_domain: int
    sender: str
    message_body: list[int]
    authority_bump: int


@dataclass
class HandleReceiveMessageParams:
    layout: typing.ClassVar = borsh.CStruct(
        "remote_domain" / borsh.U32,
        "sender" / BorshPubkey,
        "message_body" / borsh.Bytes,
        "authority_bump" / borsh.U8,
    )
    remote_domain: int
    sender: Pubkey
    message_body: bytes
    authority_bump: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "HandleReceiveMessageParams":
        return cls(
            remote_domain=obj.remote_domain,
            sender=obj.sender,
            message_body=obj.message_body,
            authority_bump=obj.authority_bump,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "remote_domain": self.remote_domain,
            "sender": self.sender,
            "message_body": self.message_body,
            "authority_bump": self.authority_bump,
        }

    def to_json(self) -> HandleReceiveMessageParamsJSON:
        return {
            "remote_domain": self.remote_domain,
            "sender": str(self.sender),
            "message_body": list(self.message_body),
            "authority_bump": self.authority_bump,
        }

    @classmethod
    def from_json(
        cls, obj: HandleReceiveMessageParamsJSON
    ) -> "HandleReceiveMessageParams":
        return cls(
            remote_domain=obj["remote_domain"],
            sender=Pubkey.from_string(obj["sender"]),
            message_body=bytes(obj["message_body"]),
            authority_bump=obj["authority_bump"],
        )
