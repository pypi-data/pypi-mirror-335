# Reference:
# https://github.com/tristeroresearch/cache-half-full/blob/main/backend/book/svm_book.py
# https://github.com/tristeroresearch/dapp/blob/dev/src/chains/solana/placeOrder.ts

from anchorpy.program.core import Program
from anchorpy.provider import Provider, Wallet
from solders.pubkey import Pubkey

from .... import config
from ....account import SolanaAccount
from ....asset import SolanaToken
from ....chain import SolanaChain
from ....chain_client import SolanaClient
from ....utility import solana
from ....transaction import SolanaTransaction
from ...types import OrderData
from .anchor import instructions
from .anchor.types import PlaceOrderParams
from .anchor.instructions import PlaceOrderAccounts
from .anchor.instructions.place_order import PlaceOrderArgs


def to_bytes_list(string: str) -> list[int]:
    return list(bytes(Pubkey.from_string(string)).rjust(32, b"\0"))


def make_order_book_program[ChainType: SolanaChain](
    program_id: Pubkey,
    client: SolanaClient[ChainType],
    account: SolanaAccount[ChainType],
) -> Program:
    wallet = Wallet(payer=account.keypair)
    provider = Provider(connection=client.native, wallet=wallet)
    return Program(idl=config.tristero_idl, program_id=program_id, provider=provider)


async def make_order_pda(program: Program, admin_panel: Pubkey) -> Pubkey:
    admin_panel_account = await program.account["AdminPanel"].fetch(admin_panel)
    order_count = admin_panel_account.order_count
    order_id_buffer = order_count.to_bytes(8, byteorder="big")
    return solana.find_program_address("order", program.program_id, (order_id_buffer,))


async def create_place_order_transaction[
    SrcChainType: SolanaChain,
](
    *,
    src_client: SolanaClient[SrcChainType],
    src_token: SolanaToken[SrcChainType],
    order_book_address: str,
    order_data: OrderData,
    account: SolanaAccount[SrcChainType],
) -> SolanaTransaction[SrcChainType]:
    program = make_order_book_program(
        program_id=Pubkey.from_string(order_book_address),
        client=src_client,
        account=account,
    )

    wallet_pubkey = account.keypair.pubkey()

    oapp = solana.find_program_address("TristeroOapp", program.program_id)

    admin_panel = solana.find_program_address("admin_panel", program.program_id)

    token_account = src_token.associated_token_account(account.keypair.pubkey())

    order_pda = await make_order_pda(program, admin_panel)

    accounts = PlaceOrderAccounts(
        authority=wallet_pubkey,
        oapp=oapp,
        admin_panel=admin_panel,
        token_mint=src_token.mint,
        token_account=token_account,
        match_account=wallet_pubkey,
        order=order_pda,
    )

    args = PlaceOrderArgs(
        params=PlaceOrderParams(
            source_sell_amount=order_data.order_funding.src_amount_in,
            min_sell_amount=order_data.order_funding.src_amount_in,
            dst_token_mint=to_bytes_list(order_data.order_direction.dst_token_address),
            dst_buy_amount=order_data.order_funding.dst_amount_out,
            eid=order_data.order_direction.dst_lzc,
            target_address=to_bytes_list(order_data.target_address),
            bond_asset_mint=Pubkey.from_string(
                order_data.order_funding.bond_token_address
            ),
            bond_amount=order_data.order_funding.bond_amount,
            bond_fee=order_data.order_funding.bond_fee,
        )
    )

    instruction = instructions.place_order(args=args, accounts=accounts)

    return await SolanaTransaction.create(
        src_client,
        (instruction,),
        (account,),
    )
