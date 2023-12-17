import asyncio

from starknet_py.contract import Contract
from starknet_py.hash.utils import message_signature
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.signer.stark_curve_signer import KeyPair

from config import BRAAVOS_ABI, RPC_URL
from utils import get_braavos_address

with open("private-key.txt", "r") as file:
    default_private_key, *_ = [row.strip() for row in file]

client = FullNodeClient(RPC_URL)


async def main():
    key_pair = KeyPair.from_private_key(default_private_key)
    address = get_braavos_address(key_pair.public_key)

    print(f'Address: {address}')

    contract = Contract(address=address, abi=BRAAVOS_ABI, provider=client, cairo_version=0)

    signer_id = 0
    message_hash = 1234

    r, s = message_signature(msg_hash=message_hash, priv_key=key_pair.private_key)

    result = await contract.functions["is_valid_signature"].call(
        message_hash,
        [signer_id, r, s]
    )

    print(result)


asyncio.run(main())
