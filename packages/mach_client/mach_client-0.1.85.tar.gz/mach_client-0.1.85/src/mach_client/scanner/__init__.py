from ..account import AccountBase
from ..asset import Token
from ..chain import Chain
from ..transaction import SentTransaction
from .scanner import Scanner


def address(chain: Chain, address: str) -> str:
    return Scanner.create(chain).address(address)


def account(account: AccountBase) -> str:
    return address(account.chain, account.address)


def transaction(transaction: SentTransaction) -> str:
    return Scanner.create(transaction.chain).transaction(transaction)


def token(token: Token) -> str:
    scanner = Scanner.create(token.chain)

    if token.is_native():
        return scanner.base_url

    return Scanner.create(token.chain).token(token)
