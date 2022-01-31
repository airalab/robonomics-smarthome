import threading
from ast import literal_eval
import serial
from substrateinterface import Keypair
import os

from utils import read_config, connect_robonomics, encrypt, add_seed_to_config


ON_SENDING = False

def _read_data_thread() -> None:
    global ON_SENDING
    keypairs, ids = read_config('python_scripts/config.config')
    data = {}
    try:
        ser = serial.Serial('/dev/ttyUSB0')
    except:
        ser = serial.Serial('/dev/ttyUSB1')
    while True:
        line = ser.readline()
        ids_list = literal_eval(ids['SDS'])
        for id in ids_list:
            if str(line[:len(id)])[2:-1] == id:
                line = str(line)
                line = line.split(':')
                data[id] = line[1][:-6].strip()
        if "Time for Sending" in str(line):
            print(f"data: {data}")
            if ON_SENDING:
                send_datalog(data)
            data = {}

def send_datalog(data: str) -> None:
    keypairs, ids = read_config('python_scripts/config.config')
    substrate = connect_robonomics()
    keypair_device = keypairs['SDS']
    try:
        user_seed = os.environ['USER_SEED']
        if user_seed[:2] == '0x':
            keypair_user = Keypair.create_from_seed(user_seed)
        else:
            keypair_user = Keypair.create_from_mnemonic(user_seed)
        seed_user = keypair_user.seed_hex
        text = encrypt(seed_user, str(data))
    except Exception as e:
        print(f"Can't encrypt message with {e}")
        text = str(data)
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

class LaunchListener:
    def __init__(self) -> None:
        print("Start reading data")
        self.substrate = connect_robonomics()
        keypairs, ids = read_config('python_scripts/config.config')
        self.keypair_device = keypairs['SDS']
        if self.keypair_device == None:
            mnemonic = Keypair.generate_mnemonic()
            self.keypair_device = Keypair.create_from_mnemonic(mnemonic, ss58_format=32)
            print(f"Generated account {self.keypair_device.ss58_address}")
            add_seed_to_config(path='python_scripts/config.config', seed=mnemonic, device='SDS')
        else:
            print(f"Your sensor address: {self.keypair_device.ss58_address}")
        threading.Thread(target=_read_data_thread).start()

    def subscription_handler(self, obj, update_nr, subscription_id) -> None:
        ch = self.substrate.get_chain_head()
        chain_events = self.substrate.get_events(ch)
        global ON_SENDING
        for ce in chain_events:
            if ce.value["event_id"] == "NewLaunch" and ce.params[1] == self.keypair_device.ss58_address:
                if ce.params[2]:
                    print(f'"ON" launch command from employer')
                    ON_SENDING = True
                else:
                    ON_SENDING = False
                    print(f'"OFF" launch command from employer')
    
    def spin(self) -> None:
        self.substrate.subscribe_block_headers(self.subscription_handler)


if __name__ == "__main__":
    s = LaunchListener()
    s.spin()