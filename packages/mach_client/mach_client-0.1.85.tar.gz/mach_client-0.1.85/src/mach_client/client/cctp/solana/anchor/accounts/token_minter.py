import typing
from dataclasses import dataclass
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from anchorpy.borsh_extension import BorshPubkey
from ..program_id import PROGRAM_ID


class TokenMinterJSON(typing.TypedDict):
    token_controller: str
    pauser: str
    paused: bool
    bump: int


@dataclass
class TokenMinter:
    discriminator: typing.ClassVar = b"z\x85T?9\x9f\xab\xce"
    layout: typing.ClassVar = borsh.CStruct(
        "token_controller" / BorshPubkey,
        "pauser" / BorshPubkey,
        "paused" / borsh.Bool,
        "bump" / borsh.U8,
    )
    token_controller: Pubkey
    pauser: Pubkey
    paused: bool
    bump: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["TokenMinter"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp.value
        if info is None:
            return None
        if info.owner != program_id:
            raise ValueError("Account does not belong to this program")
        bytes_data = info.data
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[Pubkey],
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.List[typing.Optional["TokenMinter"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["TokenMinter"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "TokenMinter":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = TokenMinter.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            token_controller=dec.token_controller,
            pauser=dec.pauser,
            paused=dec.paused,
            bump=dec.bump,
        )

    def to_json(self) -> TokenMinterJSON:
        return {
            "token_controller": str(self.token_controller),
            "pauser": str(self.pauser),
            "paused": self.paused,
            "bump": self.bump,
        }

    @classmethod
    def from_json(cls, obj: TokenMinterJSON) -> "TokenMinter":
        return cls(
            token_controller=Pubkey.from_string(obj["token_controller"]),
            pauser=Pubkey.from_string(obj["pauser"]),
            paused=obj["paused"],
            bump=obj["bump"],
        )
