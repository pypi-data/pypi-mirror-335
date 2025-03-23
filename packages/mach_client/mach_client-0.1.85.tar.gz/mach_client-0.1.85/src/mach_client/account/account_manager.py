from __future__ import annotations
import abc
from abc import ABC
import dataclasses
import typing
from typing import Optional

from ..chain import Chain, EthereumChain, SolanaChain, TronChain
from .account import Account, AccountBase, AccountID
from .hdwallet import Wallet


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class AccountIDManager(ABC):
    @abc.abstractmethod
    def get(self, chain: Chain) -> Optional[AccountID]:
        pass

    @abc.abstractmethod
    def __getitem__(self, chain: Chain) -> AccountID:
        pass

    def __contains__(self, chain: Chain) -> bool:
        return self.get(chain) is not None


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class AccountIDManagerAdapter(AccountIDManager):
    account_manager: AccountManager

    @typing.override
    def get(self, chain: Chain) -> Optional[AccountID]:
        if not (account := self.account_manager.get(chain)):
            return None

        return account.downcast()

    @typing.override
    def __getitem__(self, chain: Chain) -> AccountID:
        return self.account_manager[chain].downcast()


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class AccountManager(ABC):
    @abc.abstractmethod
    def get(self, chain: Chain) -> Optional[Account]:
        pass

    @abc.abstractmethod
    def __getitem__(self, chain: Chain) -> Account:
        pass

    def downcast(self) -> AccountIDManager:
        return AccountIDManagerAdapter(account_manager=self)

    def __contains__(self, chain: Chain) -> bool:
        return self.get(chain) is not None


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class SimpleAccountManager(AccountManager):
    private_keys: dict[type[Chain], Optional[str]]

    @classmethod
    def from_account(cls, account: Account) -> SimpleAccountManager:
        return cls(private_keys={type(account.chain): account.private_key})

    @classmethod
    def from_key_values(
        cls,
        *,
        ethereum: Optional[str] = None,
        solana: Optional[str] = None,
        tron: Optional[str] = None,
    ) -> SimpleAccountManager:
        return cls(
            private_keys={
                EthereumChain: ethereum,
                SolanaChain: solana,
                TronChain: tron,
            }
        )

    @typing.override
    def get(self, chain: Chain) -> Optional[Account]:
        chain_type = type(chain)

        if not (private_key := self.private_keys.get(chain_type)):
            return None

        return Account.from_str(chain, private_key)

    @typing.override
    def __getitem__(self, chain: Chain) -> Account:
        if not (account := self.get(chain)):
            raise KeyError(f"No private key for {chain}")

        return account


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class SimpleAccountIDManager(AccountIDManager):
    addresses: dict[type[Chain], Optional[str]]

    @classmethod
    def from_account(cls, account: AccountBase) -> SimpleAccountIDManager:
        return cls(addresses={type(account.chain): account.address})

    @classmethod
    def from_key_values(
        cls,
        *,
        ethereum: Optional[str] = None,
        solana: Optional[str] = None,
        tron: Optional[str] = None,
    ) -> SimpleAccountIDManager:
        return cls(
            addresses={
                EthereumChain: ethereum,
                SolanaChain: solana,
                TronChain: tron,
            }
        )

    @typing.override
    def get(self, chain: Chain) -> Optional[AccountID]:
        chain_type = type(chain)

        if not (address := self.addresses.get(chain_type)):
            return None

        return AccountID.from_str(chain, address)

    @typing.override
    def __getitem__(self, chain: Chain) -> AccountID:
        if not (account_id := self.get(chain)):
            raise KeyError(f"No address for {chain}")

        return account_id


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class HDWalletAccountManager(AccountManager):
    wallet: Wallet

    @typing.override
    def get(self, chain: Chain) -> Optional[Account]:
        return self[chain]

    @typing.override
    def __getitem__(self, chain: Chain) -> Account:
        return self.wallet.account(chain)
