from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class InitializeParamsJSON(typing.TypedDict):
    token_controller: str
    local_message_transmitter: str
    message_body_version: int


@dataclass
class InitializeParams:
    layout: typing.ClassVar = borsh.CStruct(
        "token_controller" / BorshPubkey,
        "local_message_transmitter" / BorshPubkey,
        "message_body_version" / borsh.U32,
    )
    token_controller: Pubkey
    local_message_transmitter: Pubkey
    message_body_version: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "InitializeParams":
        return cls(
            token_controller=obj.token_controller,
            local_message_transmitter=obj.local_message_transmitter,
            message_body_version=obj.message_body_version,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "token_controller": self.token_controller,
            "local_message_transmitter": self.local_message_transmitter,
            "message_body_version": self.message_body_version,
        }

    def to_json(self) -> InitializeParamsJSON:
        return {
            "token_controller": str(self.token_controller),
            "local_message_transmitter": str(self.local_message_transmitter),
            "message_body_version": self.message_body_version,
        }

    @classmethod
    def from_json(cls, obj: InitializeParamsJSON) -> "InitializeParams":
        return cls(
            token_controller=Pubkey.from_string(obj["token_controller"]),
            local_message_transmitter=Pubkey.from_string(
                obj["local_message_transmitter"]
            ),
            message_body_version=obj["message_body_version"],
        )
