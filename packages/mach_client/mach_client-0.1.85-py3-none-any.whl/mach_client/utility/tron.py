from tronpy import Tron


def encode_address(address: str) -> bytes:
    return bytes.fromhex(Tron.to_hex_address(address))
