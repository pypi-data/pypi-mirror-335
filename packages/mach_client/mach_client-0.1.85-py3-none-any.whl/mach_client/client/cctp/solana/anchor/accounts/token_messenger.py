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


class TokenMessengerJSON(typing.TypedDict):
    owner: str
    pending_owner: str
    local_message_transmitter: str
    message_body_version: int
    authority_bump: int


@dataclass
class TokenMessenger:
    discriminator: typing.ClassVar = b"\xa2\x04\xf24\x93\xf3\xdd`"
    layout: typing.ClassVar = borsh.CStruct(
        "owner" / BorshPubkey,
        "pending_owner" / BorshPubkey,
        "local_message_transmitter" / BorshPubkey,
        "message_body_version" / borsh.U32,
        "authority_bump" / borsh.U8,
    )
    owner: Pubkey
    pending_owner: Pubkey
    local_message_transmitter: Pubkey
    message_body_version: int
    authority_bump: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["TokenMessenger"]:
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
    ) -> typing.List[typing.Optional["TokenMessenger"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["TokenMessenger"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "TokenMessenger":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = TokenMessenger.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            owner=dec.owner,
            pending_owner=dec.pending_owner,
            local_message_transmitter=dec.local_message_transmitter,
            message_body_version=dec.message_body_version,
            authority_bump=dec.authority_bump,
        )

    def to_json(self) -> TokenMessengerJSON:
        return {
            "owner": str(self.owner),
            "pending_owner": str(self.pending_owner),
            "local_message_transmitter": str(self.local_message_transmitter),
            "message_body_version": self.message_body_version,
            "authority_bump": self.authority_bump,
        }

    @classmethod
    def from_json(cls, obj: TokenMessengerJSON) -> "TokenMessenger":
        return cls(
            owner=Pubkey.from_string(obj["owner"]),
            pending_owner=Pubkey.from_string(obj["pending_owner"]),
            local_message_transmitter=Pubkey.from_string(
                obj["local_message_transmitter"]
            ),
            message_body_version=obj["message_body_version"],
            authority_bump=obj["authority_bump"],
        )
