from __future__ import annotations
import abc
from abc import ABC
import dataclasses
import typing
from typing import Any

from ..chain import Chain


# CAIP-19 Asset Type
# https://chainagnostic.org/CAIPs/caip-19
@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class Asset[ChainType: Chain](ABC):
    @property
    @abc.abstractmethod
    def chain(self) -> ChainType:
        pass

    @property
    @abc.abstractmethod
    def asset_namespace(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def asset_reference(self) -> str:
        pass

    @property
    def id(self) -> str:
        return f"{self.chain.id}/{self.asset_namespace}:{self.asset_reference}"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Asset) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.id})"

    def __str__(self) -> str:
        return f"{self.chain}-{self.asset_reference}"


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class GenericAsset[ChainType: Chain](Asset[ChainType]):
    chain_: ChainType
    asset_namespace_: str
    asset_reference_: str

    @classmethod
    def from_id_str(cls, id: str) -> GenericAsset[ChainType]:
        chain_id, rest = id.split("/")
        chain = Chain.from_id_str(chain_id)
        asset_namespace, asset_reference = rest.split(":")
        return cls(
            chain_=chain,  # type: ignore
            asset_namespace_=asset_namespace,
            asset_reference_=asset_reference,
        )

    @property
    @typing.override
    def chain(self) -> ChainType:
        return self.chain_

    @property
    @typing.override
    def asset_namespace(self) -> str:
        return self.asset_namespace_

    @property
    @typing.override
    def asset_reference(self) -> str:
        return self.asset_reference_
