import time
import json, pycurl
from utils import read_config, connect_robonomics, decrypt

def request_sender(command: dict, url: str) -> None:
    data = json.dumps(command)
    try:
        c = pycurl.Curl()
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.HTTPHEADER, ["Content-Type: application/json"])
        c.perform()
    except Exception as e:
        print(e)

def listener(seed: str, address: str) -> None:
    substrate = connect_robonomics()
    while True:
        ch = substrate.get_chain_head()
        print(f"Chain head: {ch}")
        events = substrate.get_events(ch)
        for e in events:
            if e.value["event_id"] == "NewRecord":
                #print(f"new record {e}")
                #print(f"address {e.params[0]}")
                #print(address)
                if e.params[0] == address:
                    print(f"addr new record {e}")
                    data_encrypted = e.params[2]
                    try:
                        print(f"data: {data_encrypted}")
                        decrypted = decrypt(seed, data_encrypted)
                        print(f"decrypted {decrypted}")
                        order = json.loads(decrypted)
                        agent = order["agent"]
                        del order["agent"]
                        request_sender(order, "http://localhost:8123/api/webhook/" + agent)
                    except Exception as e:
                        print(f"Exception: {e}")
        time.sleep(12)

if __name__ == '__main__':
    config, ids = read_config('python_scripts/config.config')
    seed = config['user'].seed_hex
    address = config['user'].ss58_address
    listener(seed, address)

