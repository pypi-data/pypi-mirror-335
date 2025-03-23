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


class RemoteTokenMessengerJSON(typing.TypedDict):
    domain: int
    token_messenger: str


@dataclass
class RemoteTokenMessenger:
    discriminator: typing.ClassVar = b'is\xae"_\xe9\x8a\xfc'
    layout: typing.ClassVar = borsh.CStruct(
        "domain" / borsh.U32, "token_messenger" / BorshPubkey
    )
    domain: int
    token_messenger: Pubkey

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["RemoteTokenMessenger"]:
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
    ) -> typing.List[typing.Optional["RemoteTokenMessenger"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["RemoteTokenMessenger"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "RemoteTokenMessenger":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = RemoteTokenMessenger.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            domain=dec.domain,
            token_messenger=dec.token_messenger,
        )

    def to_json(self) -> RemoteTokenMessengerJSON:
        return {
            "domain": self.domain,
            "token_messenger": str(self.token_messenger),
        }

    @classmethod
    def from_json(cls, obj: RemoteTokenMessengerJSON) -> "RemoteTokenMessenger":
        return cls(
            domain=obj["domain"],
            token_messenger=Pubkey.from_string(obj["token_messenger"]),
        )
