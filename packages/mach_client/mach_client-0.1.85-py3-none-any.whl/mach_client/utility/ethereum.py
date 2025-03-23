from eth_typing import ChecksumAddress
from web3 import Web3


def encode_address(address: ChecksumAddress) -> bytes:
    return Web3.to_bytes(hexstr=address)
