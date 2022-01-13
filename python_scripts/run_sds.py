import threading
import time
from collections import deque
import typing as tp
from ast import literal_eval

from drivers.sds011 import SDS011
from config_sds import CONFIG
from utils import read_config, connect_robonomics, encrypt


def _read_data_thread(sensor: SDS011, q: deque) -> None:
    while True:
        meas = sensor.query()
        timestamp = int(time.time())
        q.append((meas, timestamp))


class COMStation:
    """
    Reads data from a serial port
    """

    def __init__(self) -> None:
        self.sensor = SDS011(CONFIG["port"])
        self.q = deque(maxlen=1)
        work_period = int(CONFIG["work_period"])
        self.sensor.set_work_period(work_time=int(work_period / 60))
        threading.Thread(target=_read_data_thread, args=(self.sensor, self.q)).start()

    def get_data(self) -> tp.Tuple[float, float]:
        if self.q:
            values = self.q[0]
            pm = values[0]
            pm25 = pm[0]
            pm10 = pm[1]
        print(f"Data: {pm25}, {pm10}")
        return (pm25, pm10)

    def send_datalog(self, pm25: float, pm10: float) -> str:
        config, ids = read_config('python_scripts/config.config')
        substrate = connect_robonomics()
        seed_user = config['user'].seed_hex
        keypair_device = config['SDS']
        data_ids = literal_eval(ids['SDS'])
        data = {data_ids[0]: pm25, data_ids[1]: pm10}
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


if __name__ == "__main__":
    s = COMStation()
    while True:
        time.sleep(CONFIG["work_period"])
        pm25, pm10 = s.get_data()
        s.send_datalog(pm25, pm10)