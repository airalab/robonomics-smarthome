import sys
from utils import read_config, connect_robonomics, encrypt_message
from substrateinterface import Keypair, KeypairType
from ast import literal_eval

if __name__ == '__main__':
    config, ids = read_config('python_scripts/config.config')
    substrate = connect_robonomics()
    keypair_user = Keypair.create_from_mnemonic(config['user'], crypto_type=KeypairType.ED25519)
    data = ' '.join(sys.argv[1:])
    data = data.split(' ')
    keypair_device = Keypair.create_from_mnemonic(config[data[0]], crypto_type=KeypairType.ED25519)
    name = data[0]
    data = data[1:]
    measurements = {}
    for mes in data:
        mes = mes.split(':')
        measurements[mes[0]] = mes[1]
    text = encrypt_message(str(measurements), keypair_device, keypair_user.public_key)

    print(f"Got message: {data}")
    call = substrate.compose_call(
            call_module="Datalog",
            call_function="record",
            call_params={
                'record': text
            }
        )
    extrinsic = substrate.create_signed_extrinsic(call=call, keypair=keypair_device)
    receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
    print(f"Datalog created with extrinsic hash: {receipt.extrinsic_hash}")
