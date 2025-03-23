from eth_typing import ChecksumAddress

from ... import config
from ...account import EthereumAccount
from ...chain import EthereumChain
from ...chain_client import EthereumClient
from ...transaction import EthereumTransaction
from ..types import OrderData


async def create_place_order_transaction[
    SrcChainType: EthereumChain,
](
    *,
    src_client: EthereumClient[SrcChainType],
    order_book_address: ChecksumAddress,
    order_data: OrderData,
    account: EthereumAccount[SrcChainType],
) -> EthereumTransaction[SrcChainType]:
    contract = src_client.w3.eth.contract(
        address=order_book_address,
        abi=config.ethereum_order_book_abi,
    )

    place_order_function = contract.functions.placeOrder(
        order_data.order_direction.to_eth(),
        order_data.order_funding.to_eth(),
        order_data.order_expiration.to_eth(),
        bytes.fromhex(order_data.target_address.removeprefix("0x")).rjust(32, b"\0"),
        order_data.filler_address,
    )

    return await EthereumTransaction.from_contract_function(
        src_client,
        place_order_function,
        account,
    )
