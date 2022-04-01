import robonomicsinterface as RI
from requests import get
from pinatapy import PinataPy
import typing as tp
import yaml
import os

def read_config(path: str) -> tp.Dict[str, str]:
    with open(f"{path}save-logs-config.yaml") as f:
            config = yaml.safe_load(f)
    return config

def pin_to_pinata(pinata_key: str, pinata_secret: str, file_path: str) -> str:
    pinata = PinataPy(pinata_key, pinata_secret)
    response = pinata.pin_file_to_ipfs(file_path)
    ipfs_hash = response['IpfsHash']
    print(f"Logfile pinned to ipfs with hash: {ipfs_hash}")
    return ipfs_hash

def save_logs(path: str, token: str):
    address = "localhost"
    url = f"http://{address}:8123/api/history/period"
    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    response = get(url, headers=headers)
    assert response.status_code == 200
    print("Successfully got logs")
    text = response.text
    text = text.replace('true', '"true"')
    text = text.replace('false', '"false"')
    text = text.replace('null', '"null"')
    with open(path, "w") as f:
        f.write(text)

def create_datalog(seed: str, text: str, subscription: tp.Dict[str, tp.Union[bool, str]]):
    interface = RI.RobonomicsInterface(seed=seed)
    if subscription['enable']:
        extrinsic_hash = interface.rws_record_datalog(subscription['owner'], text)
    else:
        extrinsic_hash = interface.record_datalog(text)
    print(f"Datalog created with extrinsic hash: {extrinsic_hash}")

if __name__ == '__main__':
    if __file__ != os.path.basename(__file__):
        path = __file__[:-len(os.path.basename(__file__))]
    else:
        path = os.path.realpath(__file__)[:-len(__file__)]
    log_file_path = f"{path}logs"
    config = read_config(path)
    save_logs(path=log_file_path, token=config['token'])
    ipfs_hash = pin_to_pinata(pinata_key=config['pinata_key'],
                                pinata_secret=config['pinata_secret'],
                                file_path=log_file_path)
    create_datalog(seed=config['robonomics_seed'], text=ipfs_hash)
    os.remove(log_file_path)
