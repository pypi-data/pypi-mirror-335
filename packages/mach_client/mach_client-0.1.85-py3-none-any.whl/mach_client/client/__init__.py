from __future__ import annotations
import asyncio
from datetime import datetime, timedelta
import logging
import pprint
import typing
from typing import (
    Any,
    AsyncGenerator,
    Coroutine,
    Optional,
)

from aiohttp import ClientSession, WSMsgType
import cachebox
from cachebox import Cache
from pydantic import TypeAdapter

from .. import config, log
from ..account import Account, AccountBase, AccountID, SolanaAccountID
from ..asset import ApprovableToken, NativeCoin, Token
from ..chain import Chain, constants as chain_constants
from ..chain_client import ChainClient
from ..log import LogContextAdapter, Logger
from ..utility import solana
from ..transaction import SentTransaction, Transaction
from . import cctp, order_book, utility
from .asset_server import AssetServer
from .event import (
    ApprovalFailed,
    BroadcastTransactionFailed,
    CreateTransactionFailed,
    DestinationNotReceived,
    InsufficientSourceBalance,
    OrderRejected,
    TradeEvent,
    QuoteFailed,
    QuoteLiquidityUnavailable,
    RiskManagerRejection,
    SourceNotWithdrawn,
    SubmitOrderFailed,
    Trade,
    TransactionError,
    WaitForTransactionReceiptFailed,
)
from .miles_server import MilesServerV2Mixin
from .risk_manager import RiskManager, SimilarTokenSlippageManager
from .types import (
    CCTPRequest,
    GasResponse,
    LiquiditySource,
    MachChain,
    OrderRequest,
    OrderResponse,
    Quote,
    QuoteRequest,
)


_logger = log.make_logger("mach-client", logging.INFO)


# This class is made to be used as a singleton (see below)
class MachClient(MilesServerV2Mixin):
    __slots__ = (
        "logger",
        "routes",
        "_session",
        "deployments",
        "chains",
        "tokens",
    )

    @staticmethod
    def _key_maker(_args: tuple, kwargs: dict) -> Any:
        return (
            kwargs.get("backend_url", config.config.backend.url),
            kwargs.get("logger", _logger).name,
        )

    @classmethod
    @cachebox.cached(Cache(0), key_maker=_key_maker, copy_level=2)
    async def create(
        cls,
        *,
        backend_url: str = config.config.backend.url,
        miles_url: str = config.config.miles_server.url,
        logger: Logger = _logger,
    ) -> MachClient:
        client = cls(
            backend_url=backend_url,
            miles_url=miles_url,
            logger=logger,
        )
        await client.init()
        return client

    def __init__(self, *, backend_url: str, miles_url: str, logger: Logger):
        super().__init__(miles_url)
        self.logger = logger
        self.routes = config.config.backend.endpoints.add_url(backend_url)
        self.deployments: dict[Chain, dict[str, Any]] = {}
        self.chains: set[Chain] = set()
        self.tokens: dict[Chain, set[Token]] = {}

    @property
    @typing.override
    def session(self) -> ClientSession:
        return self._session

    async def init(self) -> None:
        self._session = ClientSession()
        self.session.headers.update(
            (
                ("accept", "application/json"),
                ("Content-Type", "application/json"),
            )
        )

        await self.refresh()

    async def close(self) -> None:
        if hasattr(self, "session"):
            await self.session.close()

    async def refresh(self) -> None:
        await self.refresh_config()

    async def _process_token_data(
        self, chain_client: ChainClient, symbol: str, token_info: dict[str, Any]
    ) -> None:
        chain = chain_client.chain

        # This is the native asset, not a token
        if token_info.get("wrapped"):
            return

        self.tokens[chain].add(
            await Token.register(
                chain_client,
                token_info["address"],
                symbol,
                token_info["decimals"],
            )
        )

    async def _process_chain_data(
        self, chain_name: str, chain_data: dict[str, Any]
    ) -> Optional[tuple[Chain, dict[str, Any]]]:
        mach_chain = MachChain(chain_name)
        if not (chain := mach_chain.try_to_chain()):
            self.logger.warning(f"Chain {chain_name} is not supported")
            return

        # See note in CHAIN_TO_LAYERZERO_ID declaration
        layerzero_id = chain_data["lz_cid"]
        chain_constants.CHAIN_TO_LAYERZERO_ID[chain] = layerzero_id
        chain_constants.LAYERZERO_ID_TO_CHAIN[layerzero_id] = chain

        if cctp_domain := chain_data.get("cctp_id"):
            chain_constants.CCTP_DOMAINS[chain] = cctp_domain

        if chain not in config.config.endpoint_uris:
            self.logger.warning(f"{chain_name} endpoint URI missing from config")
            return

        result = (chain, chain_data)

        chain_client = await ChainClient.create(chain)

        self.chains.add(chain)

        if chain not in self.tokens:
            self.tokens[chain] = set()

        await asyncio.gather(
            *(
                self._process_token_data(chain_client, symbol, token_info)
                for symbol, token_info in chain_data["assets"].items()
            )
        )

        # Remove redundant data
        del chain_data["assets"]
        del chain_data["chain_id"]
        del chain_data["lz_cid"]

        return result

    async def refresh_config(self) -> None:
        async with self.session.get(self.routes.get_config) as response:
            raw_deployments: dict[str, dict[str, Any]] = (
                await utility.to_json(response)
            )["deployments"]

        result = await asyncio.gather(
            *[
                self._process_chain_data(chain_name, chain_data)
                for chain_name, chain_data in raw_deployments.items()
            ]
        )

        self.deployments = dict(filter(lambda data: data, result))  # type: ignore

    async def submit_order(
        self,
        place_order_transaction: SentTransaction,
    ) -> OrderResponse:
        order_request = OrderRequest(
            chain=MachChain.from_chain(place_order_transaction.chain),
            place_taker_tx=place_order_transaction.id,
        )

        async with self.session.post(
            self.routes.orders, json=order_request.model_dump()
        ) as response:
            bytes_result = await utility.to_bytes(response)

        return OrderResponse.model_validate_json(bytes_result)

    async def submit_cctp_order(
        self, burn_transaction: SentTransaction
    ) -> OrderResponse:
        cctp_request = CCTPRequest(
            chain=MachChain.from_chain(burn_transaction.chain),
            burn_tx=burn_transaction.id,
        )

        async with self.session.post(
            self.routes.cctp_orders, json=cctp_request.model_dump()
        ) as response:
            bytes_result = await utility.to_bytes(response)

        return OrderResponse.model_validate_json(bytes_result)

    async def watch_order_status(
        self, order: OrderResponse
    ) -> AsyncGenerator[OrderResponse]:
        url = f"{self.routes.order_status}/{order.id}"

        async with self.session.ws_connect(url) as websocket:
            async for message in websocket:
                if message.type != WSMsgType.TEXT:
                    continue

                yield OrderResponse.model_validate_json(message.data)

    async def poll_order_status(
        self, order: OrderResponse, poll_time: int
    ) -> AsyncGenerator[Optional[OrderResponse]]:
        url = f"{self.routes.order_status}/{order.id}"

        async with self.session.ws_connect(url) as websocket:
            iter = aiter(websocket)

            while True:
                try:
                    message = await asyncio.wait_for(anext(iter), timeout=poll_time)

                except TimeoutError:
                    yield None
                    continue

                except StopAsyncIteration:
                    break

                if message.type != WSMsgType.TEXT:
                    yield None

                yield OrderResponse.model_validate_json(message.data)

    _orders_validator = TypeAdapter(list[OrderResponse])

    async def get_orders(self, account: AccountBase) -> list[OrderResponse]:
        params = {
            "wallet": account.address,
        }

        async with self.session.get(self.routes.orders, params=params) as response:
            bytes_result = await utility.to_bytes(response)

        return self._orders_validator.validate_json(bytes_result)

    async def estimate_gas(self, chain: Chain) -> GasResponse:
        params = {"chain": MachChain.from_chain(chain).name}

        async with self.session.get(self.routes.gas, params=params) as response:
            bytes_result = await utility.to_bytes(response)

        return GasResponse.model_validate_json(bytes_result)

    async def request_quote(
        self,
        src_token: Token,
        dest_token: Token,
        amount: int,
        src_account: AccountBase,
        dest_account: AccountBase,
    ) -> Quote:
        assert NativeCoin not in (
            type(src_token),
            type(dest_token),
        ), "Native coins not supported"
        assert src_token.chain == src_account.chain
        assert dest_token.chain == dest_account.chain

        quote_request = QuoteRequest(
            wallet_address=src_account.address,
            target_address=dest_account.address,
            src_chain=MachChain.from_chain(src_token.chain),
            dst_chain=MachChain.from_chain(dest_token.chain),
            src_asset_address=src_token.address,
            dst_asset_address=dest_token.address,
            src_amount=amount,
        )

        async with self.session.post(
            self.routes.quotes, json=quote_request.model_dump()
        ) as response:
            bytes_result = await utility.to_bytes(response)

        return Quote.model_validate_json(bytes_result)

    def contract_address(self, chain: Chain, name: str) -> str:
        return self.deployments[chain]["contracts"][name]

    def get_contract_address(self, chain: Chain, name: str) -> Optional[str]:
        return self.deployments[chain]["contracts"].get(name)

    def order_book_address(self, chain: Chain) -> str:
        if address := self.get_contract_address(chain, "order_book_v2"):
            return address

        return self.contract_address(chain, "order_book")

    def cctp_message_transmitter_address(self, chain: Chain) -> str:
        return self.contract_address(chain, "cctp_message_transmitter")

    def cctp_token_messenger_minter_address(self, chain: Chain) -> str:
        return self.contract_address(chain, "cctp_token_messenger")

    async def place_logged_transaction(
        self,
        transaction: Transaction,
        logger: Logger,
    ) -> TransactionError | SentTransaction:
        logger.info("Broadcasting transaction")

        try:
            sent_transaction: SentTransaction = await transaction.broadcast()
        except Exception as e:
            logger.error("Failed to broadcast transaction:", exc_info=e)
            return BroadcastTransactionFailed(transaction, e, {})

        logger.info("Waiting for transaction receipt")

        try:
            receipt = await sent_transaction.wait_for_receipt()
        except Exception as e:
            logger.error(f"Could not get receipt for {sent_transaction.id}", exc_info=e)
            return WaitForTransactionReceiptFailed(sent_transaction, e, {})

        logger.info(f"Received receipt: {receipt}")

        return sent_transaction

    async def approve_token[ChainType: Chain](
        self,
        src_token: ApprovableToken[ChainType],
        account: Account[ChainType],
        spender: AccountID[ChainType],
        amount: int,
        logger: Logger,
    ) -> Optional[ApprovalFailed]:
        allowance = await src_token.get_allowance(account.downcast(), spender)

        if allowance >= amount:
            logger.debug(
                f"{spender} has allowance {src_token.format_amount(allowance)} >= required amount {src_token.format_amount(amount)}"
            )
            return

        logger.info(
            f"Placing approval transaction for {spender} to spend {src_token.format_amount(amount)}"
        )

        try:
            receipt = await src_token.approve(
                account,
                spender,
                amount,
            )
        except Exception as e:
            logger.error("Failed to create approval transaction:", exc_info=e)
            return ApprovalFailed(
                src_token,
                amount,
                account.downcast(),
                spender,
                e,
            )

        logger.info(f"Approval granted with receipt: {receipt}")

    async def place_trade[SrcChain: Chain, DestChain: Chain](
        self,
        *,
        src_token: Token[SrcChain],
        dest_token: Token[DestChain],
        amount: int,
        account: Account[SrcChain],
        recipient: AccountID[DestChain],
        risk_manager: Optional[RiskManager] = None,
        max_wait_time: timedelta = timedelta(minutes=15),
        quote: Optional[Quote] = None,
        logger: Optional[Logger] = None,
    ) -> TradeEvent:
        assert NativeCoin not in (
            type(src_token),
            type(dest_token),
        ), "Native coins not supported"
        assert src_token.chain == account.chain
        assert dest_token.chain == recipient.chain
        assert amount > 0

        if not logger:
            logger = self.logger

        logger = LogContextAdapter(logger, f"{src_token} => {dest_token}")

        if not risk_manager:
            risk_manager = SimilarTokenSlippageManager(
                config.config.trading.slippage_tolerance, logger
            )

        initial_src_balance = await src_token.get_balance(account.downcast())
        logger.debug(f"{initial_src_balance=}")

        if initial_src_balance < amount:
            logger.warning("Insufficient source balance")
            return InsufficientSourceBalance(
                src_token, initial_src_balance, account.downcast()
            )

        if not quote:
            try:
                quote = await self.request_quote(
                    src_token,
                    dest_token,
                    amount,
                    account.downcast(),
                    recipient,
                )
            except Exception as e:
                logger.error("Quote request failed:", exc_info=e)
                return QuoteFailed(
                    (src_token, dest_token), amount, account.downcast(), e
                )

        logger.info("Quote:")
        logger.info(pprint.pformat(quote))

        assert quote.src_amount == amount

        if quote.liquidity_source == LiquiditySource.unavailable:
            return QuoteLiquidityUnavailable(
                (src_token, dest_token), amount, account.downcast(), quote
            )

        elif quote.reject_order:
            return OrderRejected(
                (src_token, dest_token), amount, account.downcast(), quote
            )

        logger.info(f"Filling order through {quote.liquidity_source}")

        if (risk_analysis := await risk_manager(src_token, dest_token, quote)).reject:
            logger.warning("Order rejected by risk manager with analysis:")
            logger.warning(pprint.pformat(risk_analysis))
            return RiskManagerRejection(
                (src_token, dest_token), amount, quote, risk_analysis
            )

        src_client = await ChainClient.create(src_token.chain)

        # Needs to be computed before the order is placed
        initial_dest_balance = await dest_token.get_balance(recipient)

        error_data = {
            "pair": (src_token, dest_token),
            "quote": quote,
        }

        if quote.liquidity_source == LiquiditySource.market_maker:
            error_data.update((("type", "placeOrder"),))

            spender = AccountID.from_str(
                src_token.chain, self.order_book_address(src_token.chain)
            )

            # In the case of Solana, the spender is not the order book program itself but the oapp PDA
            if isinstance(spender, SolanaAccountID):
                spender_pubkey = solana.find_program_address(
                    "TristeroOapp", spender.pubkey
                )
                spender = SolanaAccountID(chain=spender.chain, pubkey=spender_pubkey)

            create_transaction_coro = order_book.create_place_order_transaction(
                src_client=src_client,
                src_token=src_token,
                order_data=quote.order_data,
                account=account,
            )

            def submit_order(
                sent_transaction: SentTransaction[SrcChain],
            ) -> Coroutine[Any, Any, OrderResponse]:
                return self.submit_order(sent_transaction)

        else:  # quote.liquidity_source == LiquiditySource.cctp_direct
            error_data.update((("type", "CCTP"),))

            spender = AccountID.from_str(
                src_token.chain,
                self.cctp_token_messenger_minter_address(src_token.chain),
            )

            create_transaction_coro = cctp.create_cctp_burn_transaction(
                client=self,
                src_client=src_client,
                src_token=src_token,
                dest_token=dest_token,
                order_data=quote.order_data,
                account=account,
                recipient=recipient,
            )

            def submit_order(
                sent_transaction: SentTransaction[SrcChain],
            ) -> Coroutine[Any, Any, OrderResponse]:
                return self.submit_cctp_order(sent_transaction)

        if isinstance(src_token, ApprovableToken):
            if approval_error := await self.approve_token(
                src_token, account, spender, amount, logger
            ):
                return approval_error

        logger.info(f"Placing {error_data['type']} transaction")

        try:
            transaction = await create_transaction_coro
        except Exception as e:
            logger.error(
                f"Failed to create {error_data['type']} transaction:", exc_info=e
            )
            return CreateTransactionFailed(e, error_data)

        result = await self.place_logged_transaction(transaction, logger)

        if isinstance(result, TransactionError):
            return result

        logger.info("Order placed. Submitting to backend.")

        try:
            order_response = await submit_order(result)
        except Exception as e:
            logger.error("Error submitting order to backend:", exc_info=e)
            return SubmitOrderFailed(
                (src_token, dest_token),
                amount,
                result,
                error_data,
                e,
            )

        logger.info("Order submitted to backend with response:")
        logger.info(pprint.pformat(order_response))
        logger.info("Waiting for order status updates")

        start_time = datetime.now()
        filled_at = (
            datetime.fromisoformat(order_response.filled_at)
            if order_response.filled_at
            else None
        )

        async for order in self.poll_order_status(order_response, 15):
            # Fallback on checking the token balances to determine if the order was filled or completed
            if not order:
                now = datetime.now()
                time_elapsed = now - start_time

                if filled_at:
                    received_amount = (
                        await dest_token.get_balance(recipient) - initial_dest_balance
                    )

                    if received_amount == 0:
                        if now > filled_at + max_wait_time:
                            logger.warning(
                                "Destination funds not received after max waiting time"
                            )
                            return DestinationNotReceived(
                                (src_token, dest_token),
                                amount,
                                order_response,
                                time_elapsed,
                            )

                        continue

                    elif received_amount != quote.dst_amount:
                        logger.warning(
                            f"Expected to receive {quote.dst_amount} {dest_token}, actually received {received_amount}"
                        )
                        assert received_amount > 0

                    logger.info("Order complete but websocket endpoint may be down")
                    break

                else:
                    filled_amount = initial_src_balance - await src_token.get_balance(
                        account.downcast()
                    )

                    if filled_amount == 0:
                        if now > start_time + max_wait_time:
                            logger.warning("Order not filled after max waiting time")
                            return SourceNotWithdrawn(
                                (src_token, dest_token),
                                amount,
                                order_response,
                                time_elapsed,
                            )

                        continue

                    elif filled_amount != amount:
                        logger.warning(
                            f"Expected to fill {amount} {src_token}, actually filled {filled_amount}"
                        )
                        assert filled_amount > 0

                    filled_at = now
                    logger.info("Order filled but websocket may be down")
                    continue

            if order.completed:
                break

            elif order.filled_at and not filled_at:
                filled_at = datetime.fromisoformat(order.filled_at)
                logger.info(f"Order filled at {filled_at}: {order}")

            else:
                logger.debug(f"Received order update: {order}")

        logger.info("Trade complete")

        return Trade((src_token, dest_token), quote, order_response)


__all__ = ["AssetServer", "MachClient", "RiskManager"]
