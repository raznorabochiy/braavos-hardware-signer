import asyncio
from typing import Union

from starknet_py.contract import Contract
from starknet_py.hash.address import compute_address
from starknet_py.hash.selector import get_selector_from_name

from config import BRAAVOS_IMPLEMENTATION_CLASS_HASH, BRAAVOS_PROXY_CLASS_HASH


def to_uint256(a) -> (int, int):
    return a & ((1 << 128) - 1), a >> 128


def get_braavos_address(public_key: int) -> str:
    selector = get_selector_from_name("initializer")

    calldata = [public_key]

    address = compute_address(
        class_hash=BRAAVOS_PROXY_CLASS_HASH,
        constructor_calldata=[BRAAVOS_IMPLEMENTATION_CLASS_HASH, selector, len(calldata), *calldata],
        salt=public_key,
    )

    return hex(address)


async def get_secp256r1_signer_id(contract: Contract) -> Union[int, None]:
    secp256r1_signer_type = 2
    contract_signers = await contract.functions["get_signers"].call()

    for item in contract_signers.signers:
        if item.get('signer').get('type') == secp256r1_signer_type:
            return item.get('index')

    return None
