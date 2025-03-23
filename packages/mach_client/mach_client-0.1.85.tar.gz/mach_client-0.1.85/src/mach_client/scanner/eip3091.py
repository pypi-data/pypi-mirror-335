import typing

from ..asset import Token
from ..chain import Chain, SupportedChain
from ..transaction import SentTransaction
from .scanner import Scanner


SCANNER_URLS: dict[Chain, str] = {
    SupportedChain.ETHEREUM.value: "https://etherscan.io",
    SupportedChain.OPTIMISM.value: "https://optimistic.etherscan.io",
    SupportedChain.BSC.value: "https://bscscan.com",
    SupportedChain.POLYGON.value: "https://polygonscan.com",
    SupportedChain.OPBNB.value: "https://opbnbscan.com",
    SupportedChain.MANTLE.value: "https://explorer.mantle.xyz",
    SupportedChain.BASE.value: "https://basescan.org",
    SupportedChain.MODE.value: "https://modescan.io",
    SupportedChain.ARBITRUM.value: "https://arbiscan.io",
    SupportedChain.CELO.value: "https://explorer.celo.org/mainnet",
    SupportedChain.AVALANCHE_C_CHAIN.value: "https://snowscan.xyz",
    SupportedChain.BLAST.value: "https://blastscan.io",
    SupportedChain.SCROLL.value: "https://scrollscan.com",
}


# EIP-3091 Blockchain Scanner
# https://eips.ethereum.org/EIPS/eip-3091
class EIP3091Scanner(Scanner):
    __slots__ = ("url",)

    def __init__(self, chain: Chain) -> None:
        self.url = SCANNER_URLS[chain]

    @property
    @typing.override
    def base_url(self) -> str:
        return self.url

    @typing.override
    def address(self, address: str) -> str:
        return f"{self.url}/address/{address}"

    @typing.override
    def transaction(self, transaction: SentTransaction) -> str:
        return f"{self.url}/tx/{transaction.id}"

    @typing.override
    def token(self, token: Token) -> str:
        return f"{self.url}/token/{token.address}"
