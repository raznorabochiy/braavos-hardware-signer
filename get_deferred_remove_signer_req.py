import asyncio
from datetime import datetime

from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient

from config import BRAAVOS_ABI, RPC_URL

client = FullNodeClient(RPC_URL)

with open("addresses.txt", "r") as file:
    addresses = [row.strip() for row in file]


async def main():
    for address in addresses:
        contract = Contract(address=address, abi=BRAAVOS_ABI, provider=client, cairo_version=0)
        result = await contract.functions["get_deferred_remove_signer_req"].call()
        expire_at = result[0]['expire_at']
        if expire_at > 0:
            print(address)
            print(datetime.fromtimestamp(expire_at).strftime('%d.%m.%Y %H:%M:%S'))
        print("=============")


asyncio.run(main())
