import json

RPC_URL = "https://starknet-mainnet.public.blastapi.io"
BRAAVOS_PROXY_CLASS_HASH = 0x03131fa018d520a037686ce3efddeab8f28895662f019ca3ca18a626650f7d1e
BRAAVOS_IMPLEMENTATION_CLASS_HASH = 0x5aa23d5bb71ddaa783da7ea79d405315bafa7cf0387a74f4593578c3e9e6570

with open('braavos_abi.json') as file:
    BRAAVOS_ABI = json.load(file)
