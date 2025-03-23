import abc
from abc import ABC
from typing import Optional

from aiohttp import ClientSession
from pydantic import TypeAdapter

from ... import config
from ...account import AccountBase
from .. import utility
from .types import GenerateReferralCodeResponse, Leaderboard, PointsBreakdown


class MilesServerV2Mixin(ABC):
    __slots__ = ("__routes",)

    def __init__(self, url: str) -> None:
        # The double underscore forces name mangling to occur
        # This allows subclasses to have a different `self.routes` attribute
        self.__routes = config.config.miles_server.endpoints.add_url(url)

    @property
    @abc.abstractmethod
    def session(self) -> ClientSession:
        pass

    _leaderboard_validator = TypeAdapter(Leaderboard)

    async def get_points_leaderboard(self) -> Leaderboard:
        async with self.session.get(self.__routes.leaderboard) as response:
            bytes_result = await utility.to_bytes(response)

        return self._leaderboard_validator.validate_json(bytes_result)

    async def get_points_breakdown(self, account: AccountBase) -> PointsBreakdown:
        url = f"{self.__routes.breakdown}/{account.address}"

        async with self.session.get(url) as response:
            bytes_result = await utility.to_bytes(response)

        return PointsBreakdown.model_validate_json(bytes_result)

    _referral_code_validator = TypeAdapter(Optional[str])

    async def get_bound_referral_code(self, account: AccountBase) -> Optional[str]:
        url = f"{self.__routes.bound_referral_code}/{account.address}"

        async with self.session.get(url) as response:
            bytes_result = await utility.to_bytes(response)

        return self._referral_code_validator.validate_json(bytes_result)

    async def get_generated_referral_code(self, account: AccountBase) -> Optional[str]:
        url = f"{self.__routes.generated_referral_code}/{account.address}"

        async with self.session.get(url) as response:
            bytes_result = await utility.to_bytes(response)

        return self._referral_code_validator.validate_json(bytes_result)

    async def generate_referral_code(self, account: AccountBase) -> str:
        url = f"{self.__routes.generate_referral_code}/{account.address}"

        async with self.session.post(url) as response:
            bytes_result = await utility.to_bytes(response)

        return GenerateReferralCodeResponse.model_validate_json(bytes_result).message
