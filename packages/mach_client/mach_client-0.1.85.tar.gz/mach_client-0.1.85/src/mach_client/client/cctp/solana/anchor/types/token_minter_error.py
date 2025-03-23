from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class InvalidAuthorityJSON(typing.TypedDict):
    kind: typing.Literal["InvalidAuthority"]


class InvalidTokenMinterStateJSON(typing.TypedDict):
    kind: typing.Literal["InvalidTokenMinterState"]


class ProgramPausedJSON(typing.TypedDict):
    kind: typing.Literal["ProgramPaused"]


class InvalidTokenPairStateJSON(typing.TypedDict):
    kind: typing.Literal["InvalidTokenPairState"]


class InvalidLocalTokenStateJSON(typing.TypedDict):
    kind: typing.Literal["InvalidLocalTokenState"]


class InvalidPauserJSON(typing.TypedDict):
    kind: typing.Literal["InvalidPauser"]


class InvalidTokenControllerJSON(typing.TypedDict):
    kind: typing.Literal["InvalidTokenController"]


class BurnAmountExceededJSON(typing.TypedDict):
    kind: typing.Literal["BurnAmountExceeded"]


class InvalidAmountJSON(typing.TypedDict):
    kind: typing.Literal["InvalidAmount"]


@dataclass
class InvalidAuthority:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "InvalidAuthority"

    @classmethod
    def to_json(cls) -> InvalidAuthorityJSON:
        return InvalidAuthorityJSON(
            kind="InvalidAuthority",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "InvalidAuthority": {},
        }


@dataclass
class InvalidTokenMinterState:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "InvalidTokenMinterState"

    @classmethod
    def to_json(cls) -> InvalidTokenMinterStateJSON:
        return InvalidTokenMinterStateJSON(
            kind="InvalidTokenMinterState",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "InvalidTokenMinterState": {},
        }


@dataclass
class ProgramPaused:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "ProgramPaused"

    @classmethod
    def to_json(cls) -> ProgramPausedJSON:
        return ProgramPausedJSON(
            kind="ProgramPaused",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "ProgramPaused": {},
        }


@dataclass
class InvalidTokenPairState:
    discriminator: typing.ClassVar = 3
    kind: typing.ClassVar = "InvalidTokenPairState"

    @classmethod
    def to_json(cls) -> InvalidTokenPairStateJSON:
        return InvalidTokenPairStateJSON(
            kind="InvalidTokenPairState",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "InvalidTokenPairState": {},
        }


@dataclass
class InvalidLocalTokenState:
    discriminator: typing.ClassVar = 4
    kind: typing.ClassVar = "InvalidLocalTokenState"

    @classmethod
    def to_json(cls) -> InvalidLocalTokenStateJSON:
        return InvalidLocalTokenStateJSON(
            kind="InvalidLocalTokenState",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "InvalidLocalTokenState": {},
        }


@dataclass
class InvalidPauser:
    discriminator: typing.ClassVar = 5
    kind: typing.ClassVar = "InvalidPauser"

    @classmethod
    def to_json(cls) -> InvalidPauserJSON:
        return InvalidPauserJSON(
            kind="InvalidPauser",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "InvalidPauser": {},
        }


@dataclass
class InvalidTokenController:
    discriminator: typing.ClassVar = 6
    kind: typing.ClassVar = "InvalidTokenController"

    @classmethod
    def to_json(cls) -> InvalidTokenControllerJSON:
        return InvalidTokenControllerJSON(
            kind="InvalidTokenController",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "InvalidTokenController": {},
        }


@dataclass
class BurnAmountExceeded:
    discriminator: typing.ClassVar = 7
    kind: typing.ClassVar = "BurnAmountExceeded"

    @classmethod
    def to_json(cls) -> BurnAmountExceededJSON:
        return BurnAmountExceededJSON(
            kind="BurnAmountExceeded",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "BurnAmountExceeded": {},
        }


@dataclass
class InvalidAmount:
    discriminator: typing.ClassVar = 8
    kind: typing.ClassVar = "InvalidAmount"

    @classmethod
    def to_json(cls) -> InvalidAmountJSON:
        return InvalidAmountJSON(
            kind="InvalidAmount",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "InvalidAmount": {},
        }


TokenMinterErrorKind = typing.Union[
    InvalidAuthority,
    InvalidTokenMinterState,
    ProgramPaused,
    InvalidTokenPairState,
    InvalidLocalTokenState,
    InvalidPauser,
    InvalidTokenController,
    BurnAmountExceeded,
    InvalidAmount,
]
TokenMinterErrorJSON = typing.Union[
    InvalidAuthorityJSON,
    InvalidTokenMinterStateJSON,
    ProgramPausedJSON,
    InvalidTokenPairStateJSON,
    InvalidLocalTokenStateJSON,
    InvalidPauserJSON,
    InvalidTokenControllerJSON,
    BurnAmountExceededJSON,
    InvalidAmountJSON,
]


def from_decoded(obj: dict) -> TokenMinterErrorKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "InvalidAuthority" in obj:
        return InvalidAuthority()
    if "InvalidTokenMinterState" in obj:
        return InvalidTokenMinterState()
    if "ProgramPaused" in obj:
        return ProgramPaused()
    if "InvalidTokenPairState" in obj:
        return InvalidTokenPairState()
    if "InvalidLocalTokenState" in obj:
        return InvalidLocalTokenState()
    if "InvalidPauser" in obj:
        return InvalidPauser()
    if "InvalidTokenController" in obj:
        return InvalidTokenController()
    if "BurnAmountExceeded" in obj:
        return BurnAmountExceeded()
    if "InvalidAmount" in obj:
        return InvalidAmount()
    raise ValueError("Invalid enum object")


def from_json(obj: TokenMinterErrorJSON) -> TokenMinterErrorKind:
    if obj["kind"] == "InvalidAuthority":
        return InvalidAuthority()
    if obj["kind"] == "InvalidTokenMinterState":
        return InvalidTokenMinterState()
    if obj["kind"] == "ProgramPaused":
        return ProgramPaused()
    if obj["kind"] == "InvalidTokenPairState":
        return InvalidTokenPairState()
    if obj["kind"] == "InvalidLocalTokenState":
        return InvalidLocalTokenState()
    if obj["kind"] == "InvalidPauser":
        return InvalidPauser()
    if obj["kind"] == "InvalidTokenController":
        return InvalidTokenController()
    if obj["kind"] == "BurnAmountExceeded":
        return BurnAmountExceeded()
    if obj["kind"] == "InvalidAmount":
        return InvalidAmount()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "InvalidAuthority" / borsh.CStruct(),
    "InvalidTokenMinterState" / borsh.CStruct(),
    "ProgramPaused" / borsh.CStruct(),
    "InvalidTokenPairState" / borsh.CStruct(),
    "InvalidLocalTokenState" / borsh.CStruct(),
    "InvalidPauser" / borsh.CStruct(),
    "InvalidTokenController" / borsh.CStruct(),
    "BurnAmountExceeded" / borsh.CStruct(),
    "InvalidAmount" / borsh.CStruct(),
)
