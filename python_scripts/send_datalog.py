import sys
from utils import read_config, connect_robonomics, encrypt
from ast import literal_eval

if __name__ == '__main__':
    config, ids = read_config('python_scripts/config.config')
    substrate = connect_robonomics()
    seed_user = config['user'].seed_hex
    data = ' '.join(sys.argv[1:])
    data = data.split(' ')
    keypair_device = config[data[0]]
    name = data[0]
    data = data[1:]
    measurements = {}
    for mes in data:
        mes = mes.split(':')
        measurements[mes[0]] = mes[1]
    data = {'id': name, 'data': measurements}
    text = encrypt(seed_user, str(data))

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
