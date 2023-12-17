import asyncio

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (decode_dss_signature, Prehashed)
from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.signer.stark_curve_signer import KeyPair

from config import BRAAVOS_ABI, RPC_URL
from utils import get_braavos_address, get_secp256r1_signer_id, to_uint256

with open("private-key.txt", "r") as file:
    default_private_key, *_ = [row.strip() for row in file]

with open("secp256r1-key.txt", "r") as file:
    secp256r1_private_key, *_ = [row.strip() for row in file]

client = FullNodeClient(RPC_URL)


async def main() -> None:
    key_pair = KeyPair.from_private_key(default_private_key)
    address = get_braavos_address(key_pair.public_key)

    print(f'Address: {address}')

    contract = Contract(address=address, abi=BRAAVOS_ABI, provider=client, cairo_version=0)

    secp256r1_signer = ec.derive_private_key(int(secp256r1_private_key), ec.SECP256R1())

    signer_id = await get_secp256r1_signer_id(contract)

    if signer_id is None:
        print("Can't find secp256r1 signer in account contract")
        return

    message_hash = 1234

    message_hash_bytes = message_hash.to_bytes(
        (message_hash.bit_length() + 7) // 8, byteorder="big", signed=False
    )

    message_hash_bytes_len = len(message_hash_bytes)

    signature = secp256r1_signer.sign(
        message_hash_bytes,
        ec.ECDSA(Prehashed(hashes.SHAKE256(message_hash_bytes_len))),
    )

    r, s = decode_dss_signature(signature)

    result = await contract.functions["is_valid_signature"].call(
        message_hash,
        [signer_id, *to_uint256(r), *to_uint256(s)]
    )

    print(result)


asyncio.run(main())
