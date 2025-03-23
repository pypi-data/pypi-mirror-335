from decimal import Decimal
import pprint
from typing import Any

from aiohttp import ClientResponse

from ..asset import Token
from ..chain import Chain


async def check_response(response: ClientResponse) -> Any:
    result = None

    if response.status != 200:
        try:
            result = await response.json()
        except Exception:
            result = await response.text()

        raise RuntimeError(f"API request failed:\n{response}{pprint.pformat(result)}")

    return result


async def to_json(response: ClientResponse) -> Any:
    await check_response(response)
    return await response.json()


async def to_bytes(response: ClientResponse) -> bytes:
    await check_response(response)
    return await response.read()


def chain_balances_in_coins(raw_balances: dict[Token, int]) -> dict[Token, Decimal]:
    return {token: token.to_coins(balance) for token, balance in raw_balances.items()}


def balances_in_coins(
    raw_balances: dict[Chain, dict[Token, int]],
) -> dict[Chain, dict[Token, Decimal]]:
    return {
        chain: chain_balances_in_coins(chain_balances)
        for chain, chain_balances in raw_balances.items()
    }
