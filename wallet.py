import base58
import hashlib

from ecdsa import SECP256k1
from ecdsa import SigningKey, VerifyingKey


class Wallet(object):

    def __init__(self, private_key=None):
        if private_key:
            self._private_key = SigningKey.from_string(private_key, curve=SECP256k1)
        else:
            self._private_key = SigningKey.generate(curve=SECP256k1)
        self._public_key = self._private_key.get_verifying_key()
        self.address = self.generate_address()

    @property
    def private_key(self):
        return self._private_key.to_string().hex()

    @property
    def public_key(self):
        return self._public_key.to_string().hex()

    def generate_address(self):
        public_key_bytes = self._public_key.to_string()
        public_key_prefix = bytes.fromhex("04")
        sha256_bpk = hashlib.sha256(public_key_prefix + public_key_bytes).digest()

        ripemed160_bpk = hashlib.new('ripemd160')
        ripemed160_bpk.update(sha256_bpk)
        network_byte = bytes.fromhex("00")
        ripemed160_bpk_hex = network_byte + ripemed160_bpk.digest()

        sha256_bpk = hashlib.sha256(ripemed160_bpk_hex).digest()
        sha256_2_nbpk = hashlib.sha256(sha256_bpk).digest()

        checksum = sha256_2_nbpk[:4]

        address = base58.b58encode(ripemed160_bpk_hex + checksum).decode()
        return address


class Transaction(object):

    def __init__(self, sender_private_key, sender_public_key,
                 sender_address, recipient_address,
                 amount):
        self.public_key = sender_public_key
        self.sender_address = sender_address
        self.recipient_address = recipient_address
        self.amount = amount
        self.signature = self.sign(private_key=sender_private_key)

    def sign(self, private_key):
        signing_key = SigningKey.from_string(
            bytes.fromhex(private_key), curve=SECP256k1)
        signature = signing_key.sign(self.txid)
        return signature

    def verify(self):
        signature_bytes = bytes.fromhex(self.signature)
        verifying_key = VerifyingKey.from_string(
            bytes.fromhex(self.public_key), curve=SECP256k1)
        verified_key = verifying_key.verify(signature_bytes, self._get_txid())
        return verified_key

    @property
    def txid(self):
        msg = self.sender_address + self.public_key + self.recipient_address + str(self.amount)
        msg_digest = hashlib.sha256(msg.encode()).hexdigest()
        return msg_digest

    # def generate_signature(self):
    #     sha256 = hashlib.sha256()
    #     transaction = utils.sorted_dict_by_key({
    #         'sender_blockchain_address': self.sender_blockchain_address,
    #         'recipient_blockchain_address': self.recipient_blockchain_address,
    #         'value': float(self.value)
    #     })
    #     sha256.update(str(transaction).encode('utf-8'))
    #     message = sha256.digest()
    #     private_key = SigningKey.from_string(
    #         bytes().fromhex(self.sender_private_key), curve=SECP256k1)
    #     private_key_sign = private_key.sign(message)
    #     signature = private_key_sign.hex()
    #     return signature
