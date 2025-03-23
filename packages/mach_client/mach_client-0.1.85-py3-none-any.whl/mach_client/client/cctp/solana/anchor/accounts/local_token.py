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


class LocalTokenJSON(typing.TypedDict):
    custody: str
    mint: str
    burn_limit_per_message: int
    messages_sent: int
    messages_received: int
    amount_sent: int
    amount_received: int
    bump: int
    custody_bump: int


@dataclass
class LocalToken:
    discriminator: typing.ClassVar = b"\x9f\x83:\xaa\xc1T\x80\xb6"
    layout: typing.ClassVar = borsh.CStruct(
        "custody" / BorshPubkey,
        "mint" / BorshPubkey,
        "burn_limit_per_message" / borsh.U64,
        "messages_sent" / borsh.U64,
        "messages_received" / borsh.U64,
        "amount_sent" / borsh.U128,
        "amount_received" / borsh.U128,
        "bump" / borsh.U8,
        "custody_bump" / borsh.U8,
    )
    custody: Pubkey
    mint: Pubkey
    burn_limit_per_message: int
    messages_sent: int
    messages_received: int
    amount_sent: int
    amount_received: int
    bump: int
    custody_bump: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["LocalToken"]:
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
    ) -> typing.List[typing.Optional["LocalToken"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["LocalToken"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "LocalToken":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = LocalToken.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            custody=dec.custody,
            mint=dec.mint,
            burn_limit_per_message=dec.burn_limit_per_message,
            messages_sent=dec.messages_sent,
            messages_received=dec.messages_received,
            amount_sent=dec.amount_sent,
            amount_received=dec.amount_received,
            bump=dec.bump,
            custody_bump=dec.custody_bump,
        )

    def to_json(self) -> LocalTokenJSON:
        return {
            "custody": str(self.custody),
            "mint": str(self.mint),
            "burn_limit_per_message": self.burn_limit_per_message,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "amount_sent": self.amount_sent,
            "amount_received": self.amount_received,
            "bump": self.bump,
            "custody_bump": self.custody_bump,
        }

    @classmethod
    def from_json(cls, obj: LocalTokenJSON) -> "LocalToken":
        return cls(
            custody=Pubkey.from_string(obj["custody"]),
            mint=Pubkey.from_string(obj["mint"]),
            burn_limit_per_message=obj["burn_limit_per_message"],
            messages_sent=obj["messages_sent"],
            messages_received=obj["messages_received"],
            amount_sent=obj["amount_sent"],
            amount_received=obj["amount_received"],
            bump=obj["bump"],
            custody_bump=obj["custody_bump"],
        )
