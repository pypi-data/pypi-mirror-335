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


class TokenPairJSON(typing.TypedDict):
    remote_domain: int
    remote_token: str
    local_token: str
    bump: int


@dataclass
class TokenPair:
    discriminator: typing.ClassVar = b"\x11\xd6-\xb0\xe5\x95\xc5G"
    layout: typing.ClassVar = borsh.CStruct(
        "remote_domain" / borsh.U32,
        "remote_token" / BorshPubkey,
        "local_token" / BorshPubkey,
        "bump" / borsh.U8,
    )
    remote_domain: int
    remote_token: Pubkey
    local_token: Pubkey
    bump: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["TokenPair"]:
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
    ) -> typing.List[typing.Optional["TokenPair"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["TokenPair"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "TokenPair":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = TokenPair.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            remote_domain=dec.remote_domain,
            remote_token=dec.remote_token,
            local_token=dec.local_token,
            bump=dec.bump,
        )

    def to_json(self) -> TokenPairJSON:
        return {
            "remote_domain": self.remote_domain,
            "remote_token": str(self.remote_token),
            "local_token": str(self.local_token),
            "bump": self.bump,
        }

    @classmethod
    def from_json(cls, obj: TokenPairJSON) -> "TokenPair":
        return cls(
            remote_domain=obj["remote_domain"],
            remote_token=Pubkey.from_string(obj["remote_token"]),
            local_token=Pubkey.from_string(obj["local_token"]),
            bump=obj["bump"],
        )
