from substrateinterface import SubstrateInterface, Keypair, KeypairType
import nacl.secret
import nacl.bindings
import nacl.public
import base64
import configparser
import secrets
from typing import Union

def read_config(path: str) -> dict:
    config = configparser.ConfigParser()
    config.read(path)
    sections = config.sections()
    keypairs = {}
    ids = {}
    for section in sections:
        mnemonic = config.get(section, 'SEED')
        keypairs[section] = mnemonic
    return keypairs, ids

def add_seed_to_config(path: str, seed: str, device: str) -> None:
    config = configparser.ConfigParser()
    config.read(path)
    config[device]['SEED'] = seed
    with open(path, 'w') as configfile:
        config.write(configfile)


def connect_robonomics() -> SubstrateInterface:
    substrate = SubstrateInterface(
            url="wss://kusama.rpc.robonomics.network",
            ss58_format=32,
            type_registry_preset="substrate-node-template",
            type_registry= {
                "types": {
                    "Record": "Vec<u8>",
                    "Parameter": "Bool",
                    "LaunchParameter": "Bool",
                    "<T as frame_system::Config>::AccountId": "AccountId",
                    "RingBufferItem": {
                        "type": "struct",
                        "type_mapping": [["timestamp", "Compact<u64>"], ["payload", "Vec<u8>"]],
                    },
                    "RingBufferIndex": {
                        "type": "struct",
                        "type_mapping": [["start", "Compact<u64>"], ["end", "Compact<u64>"]],
                    },
                }
            }
            )
    return substrate

def encrypt_message(
    message: Union[bytes, str], sender_keypair: Keypair, recipient_public_key: bytes, nonce: bytes = secrets.token_bytes(24),
) -> bytes:
    curve25519_public_key = nacl.bindings.crypto_sign_ed25519_pk_to_curve25519(recipient_public_key)
    recipient = nacl.public.PublicKey(curve25519_public_key)
    private_key = nacl.bindings.crypto_sign_ed25519_sk_to_curve25519(sender_keypair.private_key + sender_keypair.public_key)
    sender = nacl.public.PrivateKey(private_key)
    box = nacl.public.Box(sender, recipient)
    encrypted = box.encrypt(message if isinstance(message, bytes) else message.encode("utf-8"), nonce)
    return base64.b64encode(encrypted).decode("ascii")

def decrypt_message(encrypted_message: bytes, sender_public_key: bytes, recipient_keypair: Keypair) -> bytes:
    private_key = nacl.bindings.crypto_sign_ed25519_sk_to_curve25519(recipient_keypair.private_key + recipient_keypair.public_key)
    recipient = nacl.public.PrivateKey(private_key)
    curve25519_public_key = nacl.bindings.crypto_sign_ed25519_pk_to_curve25519(sender_public_key)
    sender = nacl.public.PublicKey(curve25519_public_key)
    encrypted = base64.b64decode(encrypted_message)
    return nacl.public.Box(recipient, sender).decrypt(encrypted)
