import typing
from anchorpy.error import ProgramError


class InvalidAuthority(ProgramError):
    def __init__(self) -> None:
        super().__init__(6000, "Invalid Authority")

    code = 6000
    name = "InvalidAuthority"
    msg = "Invalid Authority"


class InvalidTokenOwner(ProgramError):
    def __init__(self) -> None:
        super().__init__(6001, "InvalidTokenOwner")

    code = 6001
    name = "InvalidTokenOwner"
    msg = "InvalidTokenOwner"


class InvalidTokenMintAddress(ProgramError):
    def __init__(self) -> None:
        super().__init__(6002, "InvalidTokenMintAddress")

    code = 6002
    name = "InvalidTokenMintAddress"
    msg = "InvalidTokenMintAddress"


class InvalidTokenAmount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6003, "InvalidTokenAmount")

    code = 6003
    name = "InvalidTokenAmount"
    msg = "InvalidTokenAmount"


class InvalidOwnerWithTradeMatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(6004, "InvalidOwnerWithTradeMatch")

    code = 6004
    name = "InvalidOwnerWithTradeMatch"
    msg = "InvalidOwnerWithTradeMatch"


class InvalidTradeMatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(6005, "InvalidTradeMatch")

    code = 6005
    name = "InvalidTradeMatch"
    msg = "InvalidTradeMatch"


class InvalidTokenStandard(ProgramError):
    def __init__(self) -> None:
        super().__init__(6006, "InvalidTokenStandard")

    code = 6006
    name = "InvalidTokenStandard"
    msg = "InvalidTokenStandard"


class PayloadHashNotFound(ProgramError):
    def __init__(self) -> None:
        super().__init__(6007, "PayloadHashNotFound")

    code = 6007
    name = "PayloadHashNotFound"
    msg = "PayloadHashNotFound"


class NotAgain(ProgramError):
    def __init__(self) -> None:
        super().__init__(6008, "Already canceled or traded")

    code = 6008
    name = "NotAgain"
    msg = "Already canceled or traded"


class NotEvenStarted(ProgramError):
    def __init__(self) -> None:
        super().__init__(6009, "Not even started")

    code = 6009
    name = "NotEvenStarted"
    msg = "Not even started"


class WrongMsgTypeError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6010, "Wrong msg type")

    code = 6010
    name = "WrongMsgTypeError"
    msg = "Wrong msg type"


class WrongMsgDstIndex(ProgramError):
    def __init__(self) -> None:
        super().__init__(6011, "Can not find with dst index")

    code = 6011
    name = "WrongMsgDstIndex"
    msg = "Can not find with dst index"


class WrongMsgSrcToken(ProgramError):
    def __init__(self) -> None:
        super().__init__(6012, "Can not find with src token address")

    code = 6012
    name = "WrongMsgSrcToken"
    msg = "Can not find with src token address"


class WrongMsgDstToken(ProgramError):
    def __init__(self) -> None:
        super().__init__(6013, "Can not find with dst token address")

    code = 6013
    name = "WrongMsgDstToken"
    msg = "Can not find with dst token address"


class WrongAuthorityToCancel(ProgramError):
    def __init__(self) -> None:
        super().__init__(6014, "Can not cancel with this authority")

    code = 6014
    name = "WrongAuthorityToCancel"
    msg = "Can not cancel with this authority"


class MinSellAmountConflict(ProgramError):
    def __init__(self) -> None:
        super().__init__(6015, "Min Sell Amount Conflict")

    code = 6015
    name = "MinSellAmountConflict"
    msg = "Min Sell Amount Conflict"


class InSufficientFundsOfOrder(ProgramError):
    def __init__(self) -> None:
        super().__init__(6016, "Insufficient Funds of Order")

    code = 6016
    name = "InSufficientFundsOfOrder"
    msg = "Insufficient Funds of Order"


class TokenNotApproved(ProgramError):
    def __init__(self) -> None:
        super().__init__(6017, "Token Not Approved")

    code = 6017
    name = "TokenNotApproved"
    msg = "Token Not Approved"


class InsufficientApproval(ProgramError):
    def __init__(self) -> None:
        super().__init__(6018, "Insufficient Approval")

    code = 6018
    name = "InsufficientApproval"
    msg = "Insufficient Approval"


class OrderNotValid(ProgramError):
    def __init__(self) -> None:
        super().__init__(6019, "Order Not Valid")

    code = 6019
    name = "OrderNotValid"
    msg = "Order Not Valid"


class OrderAlreadyMatched(ProgramError):
    def __init__(self) -> None:
        super().__init__(6020, "Order Already Matched")

    code = 6020
    name = "OrderAlreadyMatched"
    msg = "Order Already Matched"


class MatchAlreadyFinalized(ProgramError):
    def __init__(self) -> None:
        super().__init__(6021, "Match Already Finalized")

    code = 6021
    name = "MatchAlreadyFinalized"
    msg = "Match Already Finalized"


class ArithmeticError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6022, "Arithmetic Error")

    code = 6022
    name = "ArithmeticError"
    msg = "Arithmetic Error"


class InsufficientOrderAmount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6023, "Insufficient Order Amount")

    code = 6023
    name = "InsufficientOrderAmount"
    msg = "Insufficient Order Amount"


class InvalidSendLibrary(ProgramError):
    def __init__(self) -> None:
        super().__init__(6024, None)

    code = 6024
    name = "InvalidSendLibrary"
    msg = None


class InvalidReceiveLibrary(ProgramError):
    def __init__(self) -> None:
        super().__init__(6025, None)

    code = 6025
    name = "InvalidReceiveLibrary"
    msg = None


class SameValue(ProgramError):
    def __init__(self) -> None:
        super().__init__(6026, None)

    code = 6026
    name = "SameValue"
    msg = None


class AccountNotFound(ProgramError):
    def __init__(self) -> None:
        super().__init__(6027, None)

    code = 6027
    name = "AccountNotFound"
    msg = None


class OnlySendLib(ProgramError):
    def __init__(self) -> None:
        super().__init__(6028, None)

    code = 6028
    name = "OnlySendLib"
    msg = None


class OnlyReceiveLib(ProgramError):
    def __init__(self) -> None:
        super().__init__(6029, None)

    code = 6029
    name = "OnlyReceiveLib"
    msg = None


class InvalidExpiry(ProgramError):
    def __init__(self) -> None:
        super().__init__(6030, None)

    code = 6030
    name = "InvalidExpiry"
    msg = None


class OnlyNonDefaultLib(ProgramError):
    def __init__(self) -> None:
        super().__init__(6031, None)

    code = 6031
    name = "OnlyNonDefaultLib"
    msg = None


class InvalidAmount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6032, None)

    code = 6032
    name = "InvalidAmount"
    msg = None


class InvalidNonce(ProgramError):
    def __init__(self) -> None:
        super().__init__(6033, None)

    code = 6033
    name = "InvalidNonce"
    msg = None


class Unauthorized(ProgramError):
    def __init__(self) -> None:
        super().__init__(6034, None)

    code = 6034
    name = "Unauthorized"
    msg = None


class ComposeNotFound(ProgramError):
    def __init__(self) -> None:
        super().__init__(6035, None)

    code = 6035
    name = "ComposeNotFound"
    msg = None


class InvalidPayloadHash(ProgramError):
    def __init__(self) -> None:
        super().__init__(6036, None)

    code = 6036
    name = "InvalidPayloadHash"
    msg = None


class LzTokenUnavailable(ProgramError):
    def __init__(self) -> None:
        super().__init__(6037, None)

    code = 6037
    name = "LzTokenUnavailable"
    msg = None


class ReadOnlyAccount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6038, None)

    code = 6038
    name = "ReadOnlyAccount"
    msg = None


class InvalidMessageLib(ProgramError):
    def __init__(self) -> None:
        super().__init__(6039, None)

    code = 6039
    name = "InvalidMessageLib"
    msg = None


class WritableAccountNotAllowed(ProgramError):
    def __init__(self) -> None:
        super().__init__(6040, None)

    code = 6040
    name = "WritableAccountNotAllowed"
    msg = None


CustomError = typing.Union[
    InvalidAuthority,
    InvalidTokenOwner,
    InvalidTokenMintAddress,
    InvalidTokenAmount,
    InvalidOwnerWithTradeMatch,
    InvalidTradeMatch,
    InvalidTokenStandard,
    PayloadHashNotFound,
    NotAgain,
    NotEvenStarted,
    WrongMsgTypeError,
    WrongMsgDstIndex,
    WrongMsgSrcToken,
    WrongMsgDstToken,
    WrongAuthorityToCancel,
    MinSellAmountConflict,
    InSufficientFundsOfOrder,
    TokenNotApproved,
    InsufficientApproval,
    OrderNotValid,
    OrderAlreadyMatched,
    MatchAlreadyFinalized,
    ArithmeticError,
    InsufficientOrderAmount,
    InvalidSendLibrary,
    InvalidReceiveLibrary,
    SameValue,
    AccountNotFound,
    OnlySendLib,
    OnlyReceiveLib,
    InvalidExpiry,
    OnlyNonDefaultLib,
    InvalidAmount,
    InvalidNonce,
    Unauthorized,
    ComposeNotFound,
    InvalidPayloadHash,
    LzTokenUnavailable,
    ReadOnlyAccount,
    InvalidMessageLib,
    WritableAccountNotAllowed,
]
CUSTOM_ERROR_MAP: dict[int, CustomError] = {
    6000: InvalidAuthority(),
    6001: InvalidTokenOwner(),
    6002: InvalidTokenMintAddress(),
    6003: InvalidTokenAmount(),
    6004: InvalidOwnerWithTradeMatch(),
    6005: InvalidTradeMatch(),
    6006: InvalidTokenStandard(),
    6007: PayloadHashNotFound(),
    6008: NotAgain(),
    6009: NotEvenStarted(),
    6010: WrongMsgTypeError(),
    6011: WrongMsgDstIndex(),
    6012: WrongMsgSrcToken(),
    6013: WrongMsgDstToken(),
    6014: WrongAuthorityToCancel(),
    6015: MinSellAmountConflict(),
    6016: InSufficientFundsOfOrder(),
    6017: TokenNotApproved(),
    6018: InsufficientApproval(),
    6019: OrderNotValid(),
    6020: OrderAlreadyMatched(),
    6021: MatchAlreadyFinalized(),
    6022: ArithmeticError(),
    6023: InsufficientOrderAmount(),
    6024: InvalidSendLibrary(),
    6025: InvalidReceiveLibrary(),
    6026: SameValue(),
    6027: AccountNotFound(),
    6028: OnlySendLib(),
    6029: OnlyReceiveLib(),
    6030: InvalidExpiry(),
    6031: OnlyNonDefaultLib(),
    6032: InvalidAmount(),
    6033: InvalidNonce(),
    6034: Unauthorized(),
    6035: ComposeNotFound(),
    6036: InvalidPayloadHash(),
    6037: LzTokenUnavailable(),
    6038: ReadOnlyAccount(),
    6039: InvalidMessageLib(),
    6040: WritableAccountNotAllowed(),
}


def from_code(code: int) -> typing.Optional[CustomError]:
    maybe_err = CUSTOM_ERROR_MAP.get(code)
    if maybe_err is None:
        return None
    return maybe_err
