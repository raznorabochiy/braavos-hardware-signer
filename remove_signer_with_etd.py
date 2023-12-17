import asyncio

from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair

from config import BRAAVOS_ABI, RPC_URL
from utils import get_braavos_address, get_secp256r1_signer_id

with open("private-key.txt", "r") as file:
    default_private_key, *_ = [row.strip() for row in file]

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

    signer_id = await get_secp256r1_signer_id(contract)

    if signer_id is None:
        print("Can't find secp256r1 signer in account contract")
        return

    add_signer_call = contract.functions["remove_signer_with_etd"].prepare(signer_id)
    tx = await account.execute(calls=add_signer_call, auto_estimate=True)

    print(f'https://voyager.online/tx/{hex(tx.transaction_hash)}')
    print('=============')


asyncio.run(main())
