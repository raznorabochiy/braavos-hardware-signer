from typing import List, cast

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (Prehashed, decode_dss_signature)
from starknet_py.constants import DEFAULT_ENTRY_POINT_SELECTOR
from starknet_py.hash.transaction import (
    TransactionHashPrefix,
    compute_transaction_hash,
)
from starknet_py.net.models import AddressRepresentation, StarknetChainId, parse_address
from starknet_py.net.models.transaction import (
    AccountTransaction,
    Declare,
    DeclareV2,
    DeployAccount,
    Invoke,
)
from starknet_py.net.signer.base_signer import BaseSigner
from starknet_py.utils.typed_data import TypedData

from utils import to_uint256


class Secp256rSigner(BaseSigner):
    def __init__(
            self,
            signer_id: int,
            account_address: AddressRepresentation,
            key_pair: ec.EllipticCurvePrivateKey,
            chain_id: StarknetChainId,
    ):
        """
        :param signer_id: id of Hardware Signer in account contract
        :param account_address: Address of the account contract.
        :param key_pair: Key pair of the account contract.
        :param chain_id: ChainId of the chain.
        """
        self.signer_id = signer_id
        self.address = parse_address(account_address)
        self.key_pair = key_pair
        self.chain_id = chain_id

    @property
    def private_key(self) -> int:
        """Private key of the signer."""
        return self.key_pair.private_numbers().private_value

    @property
    def public_key(self) -> int:
        return self.key_pair.public_key().public_numbers().x

    def sign_transaction(
            self,
            transaction: AccountTransaction,
    ) -> List[int]:
        if isinstance(transaction, Declare):
            raise Exception("Declare transaction not supported")
        if isinstance(transaction, DeclareV2):
            raise Exception("DeclareV2 transaction not supported")
        if isinstance(transaction, DeployAccount):
            raise Exception("DeployAccount transaction not supported")
        return self._sign_transaction(cast(Invoke, transaction))

    def _sign_transaction(self, transaction: Invoke):
        tx_hash = compute_transaction_hash(
            tx_hash_prefix=TransactionHashPrefix.INVOKE,
            version=transaction.version,
            contract_address=self.address,
            entry_point_selector=DEFAULT_ENTRY_POINT_SELECTOR,
            calldata=transaction.calldata,
            max_fee=transaction.max_fee,
            chain_id=self.chain_id,
            additional_data=[transaction.nonce],
        )

        r, s = self._sign(tx_hash)
        return [self.signer_id, *to_uint256(r), *to_uint256(s)]

    def sign_message(self, typed_data: TypedData, account_address: int) -> List[int]:
        msg_hash = typed_data.message_hash(account_address)

        r, s = self._sign(msg_hash)
        return [self.signer_id, *to_uint256(r), *to_uint256(s)]

    def _sign(self, hashed_msg: int) -> tuple[int, int]:
        hashed_msg_bytes = hashed_msg.to_bytes(
            (hashed_msg.bit_length() + 7) // 8, byteorder="big", signed=False
        )

        signature = self.key_pair.sign(
            hashed_msg_bytes,
            ec.ECDSA(Prehashed(hashes.SHAKE256(len(hashed_msg_bytes)))),
        )

        return decode_dss_signature(signature)
