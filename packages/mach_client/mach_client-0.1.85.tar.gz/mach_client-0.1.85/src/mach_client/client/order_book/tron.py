import typing

from tronpy.async_contract import AsyncContractMethod

from ... import config
from ...account import TronAccount
from ...chain import TronChain
from ...chain_client import TronClient
from ...transaction import TronTransaction
from ..types import OrderData


async def create_place_order_transaction[SrcChainType: TronChain](
    *,
    src_client: TronClient[SrcChainType],
    order_book_address: str,
    order_data: OrderData,
    account: TronAccount[SrcChainType],
) -> TronTransaction[SrcChainType]:
    contract = await src_client.native.get_contract(order_book_address)
    contract.abi = config.tron_order_book_abi

    return await TronTransaction.from_contract_method(
        src_client,
        account,
        typing.cast(AsyncContractMethod, contract.functions.placeOrder),
        order_data.order_direction.to_tron(),
        order_data.order_funding.to_tron(),
        order_data.order_expiration.to_tron(),
        # TODO: bytes32
        order_data.target_address,
        order_data.filler_address,
    )
