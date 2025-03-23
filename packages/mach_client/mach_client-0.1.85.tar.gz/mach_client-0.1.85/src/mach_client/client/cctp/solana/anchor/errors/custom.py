import typing
from anchorpy.error import ProgramError


class InvalidAuthority(ProgramError):
    def __init__(self) -> None:
        super().__init__(6000, "Invalid authority")

    code = 6000
    name = "InvalidAuthority"
    msg = "Invalid authority"


class InvalidTokenMessengerState(ProgramError):
    def __init__(self) -> None:
        super().__init__(6001, "Invalid token messenger state")

    code = 6001
    name = "InvalidTokenMessengerState"
    msg = "Invalid token messenger state"


class InvalidTokenMessenger(ProgramError):
    def __init__(self) -> None:
        super().__init__(6002, "Invalid token messenger")

    code = 6002
    name = "InvalidTokenMessenger"
    msg = "Invalid token messenger"


class InvalidOwner(ProgramError):
    def __init__(self) -> None:
        super().__init__(6003, "Invalid owner")

    code = 6003
    name = "InvalidOwner"
    msg = "Invalid owner"


class MalformedMessage(ProgramError):
    def __init__(self) -> None:
        super().__init__(6004, "Malformed message")

    code = 6004
    name = "MalformedMessage"
    msg = "Malformed message"


class InvalidMessageBodyVersion(ProgramError):
    def __init__(self) -> None:
        super().__init__(6005, "Invalid message body version")

    code = 6005
    name = "InvalidMessageBodyVersion"
    msg = "Invalid message body version"


class InvalidAmount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6006, "Invalid amount")

    code = 6006
    name = "InvalidAmount"
    msg = "Invalid amount"


class InvalidDestinationDomain(ProgramError):
    def __init__(self) -> None:
        super().__init__(6007, "Invalid destination domain")

    code = 6007
    name = "InvalidDestinationDomain"
    msg = "Invalid destination domain"


class InvalidDestinationCaller(ProgramError):
    def __init__(self) -> None:
        super().__init__(6008, "Invalid destination caller")

    code = 6008
    name = "InvalidDestinationCaller"
    msg = "Invalid destination caller"


class InvalidMintRecipient(ProgramError):
    def __init__(self) -> None:
        super().__init__(6009, "Invalid mint recipient")

    code = 6009
    name = "InvalidMintRecipient"
    msg = "Invalid mint recipient"


class InvalidSender(ProgramError):
    def __init__(self) -> None:
        super().__init__(6010, "Invalid sender")

    code = 6010
    name = "InvalidSender"
    msg = "Invalid sender"


class InvalidTokenPair(ProgramError):
    def __init__(self) -> None:
        super().__init__(6011, "Invalid token pair")

    code = 6011
    name = "InvalidTokenPair"
    msg = "Invalid token pair"


class InvalidTokenMint(ProgramError):
    def __init__(self) -> None:
        super().__init__(6012, "Invalid token mint")

    code = 6012
    name = "InvalidTokenMint"
    msg = "Invalid token mint"


CustomError = typing.Union[
    InvalidAuthority,
    InvalidTokenMessengerState,
    InvalidTokenMessenger,
    InvalidOwner,
    MalformedMessage,
    InvalidMessageBodyVersion,
    InvalidAmount,
    InvalidDestinationDomain,
    InvalidDestinationCaller,
    InvalidMintRecipient,
    InvalidSender,
    InvalidTokenPair,
    InvalidTokenMint,
]
CUSTOM_ERROR_MAP: dict[int, CustomError] = {
    6000: InvalidAuthority(),
    6001: InvalidTokenMessengerState(),
    6002: InvalidTokenMessenger(),
    6003: InvalidOwner(),
    6004: MalformedMessage(),
    6005: InvalidMessageBodyVersion(),
    6006: InvalidAmount(),
    6007: InvalidDestinationDomain(),
    6008: InvalidDestinationCaller(),
    6009: InvalidMintRecipient(),
    6010: InvalidSender(),
    6011: InvalidTokenPair(),
    6012: InvalidTokenMint(),
}


def from_code(code: int) -> typing.Optional[CustomError]:
    maybe_err = CUSTOM_ERROR_MAP.get(code)
    if maybe_err is None:
        return None
    return maybe_err
