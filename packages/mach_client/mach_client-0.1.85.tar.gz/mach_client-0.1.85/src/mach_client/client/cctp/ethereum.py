import typing

from eth_typing import ChecksumAddress

from ... import config
from ...account import EthereumAccount
from ...chain import EthereumChain
from ...chain_client import EthereumClient
from ...transaction import EthereumTransaction
from ..types import OrderData


async def create_cctp_burn_transaction[SrcChainType: EthereumChain](
    *,
    src_client: EthereumClient[SrcChainType],
    destination_domain: int,
    token_messenger_minter_address: str,
    order_data: OrderData,
    account: EthereumAccount[SrcChainType],
    recipient: bytes,
) -> EthereumTransaction[SrcChainType]:
    contract = src_client.w3.eth.contract(
        address=typing.cast(ChecksumAddress, token_messenger_minter_address),
        abi=config.ethereum_cctp_token_messenger_abi,
    )

    burn_function = contract.functions.depositForBurn(
        order_data.order_funding.src_amount_in,
        destination_domain,
        recipient,
        order_data.order_direction.src_token_address,
    )

    return await EthereumTransaction.from_contract_function(
        src_client, burn_function, account
    )
