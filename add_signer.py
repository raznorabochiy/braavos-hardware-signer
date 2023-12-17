import asyncio

from cryptography.hazmat.primitives.asymmetric import ec
from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair

from config import BRAAVOS_ABI, RPC_URL
from utils import get_braavos_address, to_uint256

with open("private-key.txt", "r") as file:
    default_private_key, *_ = [row.strip() for row in file]

with open("secp256r1-key.txt", "r") as file:
    secp256r1_private_key, *_ = [row.strip() for row in file]

client = FullNodeClient(RPC_URL)


async def main():
    key_pair = KeyPair.from_private_key(default_private_key)
    address = get_braavos_address(key_pair.public_key)

    print(f'Address: {address}')

    account = Account(
        address=address,
        client=client,
        key_pair=key_pair,
        chain=StarknetChainId.MAINNET,
    )

    contract = Contract(address=address, abi=BRAAVOS_ABI, provider=account, cairo_version=0)

    secp256r1_signer = ec.derive_private_key(int(secp256r1_private_key), ec.SECP256R1())
    public_numbers = secp256r1_signer.public_key().public_numbers()

    x_uint256 = to_uint256(public_numbers.x)
    y_uint256 = to_uint256(public_numbers.y)

    secp256r1_signer_type = 2

    signer_model = {
        'signer_0': x_uint256[0],
        'signer_1': x_uint256[1],
        'signer_2': y_uint256[0],
        'signer_3': y_uint256[1],
        'type': secp256r1_signer_type,
        'reserved_0': 0,
        'reserved_1': 0,
    }

    add_signer_call = contract.functions["add_signer"].prepare(signer_model)
    tx = await account.execute(calls=add_signer_call, auto_estimate=True)

    print(f'https://voyager.online/tx/{hex(tx.transaction_hash)}')


asyncio.run(main())
