from __future__ import annotations
import dataclasses

from hdwallet import HDWallet
from hdwallet.const import PUBLIC_KEY_TYPES
from hdwallet.cryptocurrencies import Bitcoin, Ethereum, ICryptocurrency, Solana, Tron
from hdwallet.derivations import BIP44Derivation, CustomDerivation
from hdwallet.entropies import BIP39_ENTROPY_STRENGTHS, BIP39Entropy
from hdwallet.hds import BIP32HD, BIP44HD, IHD
from hdwallet.mnemonics import BIP39Mnemonic

from ..chain import Chain, EthereumChain, SolanaChain, TronChain
from .account import Account, AccountID


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class Wallet:
    mnemonic: str

    @staticmethod
    def create_base_hdwallet(
        cryptocurrency: type[ICryptocurrency] = Bitcoin,
        hd: type[IHD] = BIP44HD,
    ) -> HDWallet:
        return HDWallet(
            cryptocurrency=cryptocurrency,
            hd=hd,
            network=cryptocurrency.NETWORKS.MAINNET,
            public_key_type=PUBLIC_KEY_TYPES.COMPRESSED,
        )

    @classmethod
    def create(cls) -> Wallet:
        hdwallet = cls.create_base_hdwallet().from_entropy(
            entropy=BIP39Entropy(
                entropy=BIP39Entropy.generate(
                    strength=BIP39_ENTROPY_STRENGTHS.TWO_HUNDRED_FIFTY_SIX
                )
            )
        )

        return cls(mnemonic=hdwallet.mnemonic())  # type: ignore

    # Check if the mnemonic is valid
    @classmethod
    def from_mnemonic(cls, mnemonic: str) -> Wallet:
        hdwallet = cls.create_base_hdwallet().from_mnemonic(
            mnemonic=BIP39Mnemonic(mnemonic=mnemonic)
        )
        return cls(mnemonic=hdwallet.mnemonic())  # type: ignore

    def create_hdwallet(
        self,
        cryptocurrency: type[ICryptocurrency] = Bitcoin,
        hd: type[IHD] = BIP44HD,
    ) -> HDWallet:
        return self.create_base_hdwallet(cryptocurrency, hd).from_mnemonic(
            mnemonic=BIP39Mnemonic(mnemonic=self.mnemonic)
        )

    @property
    def xprivate_key(self) -> str:
        return self.create_hdwallet().root_xprivate_key()  # type: ignore

    @property
    def xpublic_key(self) -> str:
        return self.create_hdwallet().root_xpublic_key()  # type: ignore

    # Derive the default address for the chain
    def derive_default(self, chain: Chain) -> HDWallet:
        match chain:
            case EthereumChain():
                cryptocurrency = Ethereum

                # Notice that we use the base coin type for Ethereum instead of the chain's coin type
                # So ie. BSC will use the same derivation path as Ethereum
                # This is to ensure that as many chains use the same keypair as possible
                return self.create_hdwallet(cryptocurrency).from_derivation(
                    derivation=BIP44Derivation(coin_type=cryptocurrency.COIN_TYPE)
                )

            case SolanaChain():
                cryptocurrency = Solana

                # https://github.com/talonlab/python-hdwallet/issues/109
                return self.create_hdwallet(cryptocurrency, BIP32HD).from_derivation(
                    derivation=CustomDerivation(
                        path=f"m/44'/{cryptocurrency.COIN_TYPE}'/0'/0'"
                    )
                )

            case TronChain():
                cryptocurrency = Tron

                return self.create_hdwallet(cryptocurrency).from_derivation(
                    derivation=BIP44Derivation(coin_type=cryptocurrency.COIN_TYPE)
                )

            case _:
                assert False, f"Unsupported chain: {chain} with type {type(chain)}"

    def account[ChainType: Chain](self, chain: ChainType) -> Account[ChainType]:
        hdwallet = self.derive_default(chain)
        return Account.from_hdwallet(chain, hdwallet)

    def account_id[ChainType: Chain](self, chain: ChainType) -> AccountID[ChainType]:
        hdwallet = self.derive_default(chain)
        return AccountID.from_hdwallet(chain, hdwallet)
