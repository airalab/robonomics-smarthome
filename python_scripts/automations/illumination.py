from requests import get, post
import time
import yaml
import os
import typing as tp
from datetime import datetime
from ast import literal_eval
import logging

logging.basicConfig(level=logging.INFO)

class IlluminationAutomation:
    def __init__(self) -> None:
        if __file__ != os.path.basename(__file__):
            self.path = __file__[:-len(os.path.basename(__file__))]
        else:
            self.path = os.path.realpath(__file__)[:-len(__file__)]
        logging.debug(f"Script path is {self.path}")
        with open(f"{self.path}illumination_config.yaml") as f:
            self.config = yaml.safe_load(f)
        logging.debug(f"Config is {self.config}")
        try:
            with open(f"{self.path}data/illumination.yaml") as f:
                self.data = yaml.safe_load(f)
        except FileNotFoundError:
            with open(f"{self.path}data/illumination.yaml", "w") as f:
                date = datetime.today()
                self.data = {'mkmol': 0, 'date': date.day}
                yaml.dump(self.data, f)
        logging.debug(f"Data file: {self.data}")
        if (self.config['sensor_id'] is None) or (self.config['light_socket_id'] is None):
            self.choose_entities()
    
    def choose_entities(self) -> None:
        logging.debug("Start choose entities")
        response = self.get_request("states")
        sensors = []
        lamps = []
        for entity in response:
            entity_id = entity["entity_id"]
            entity_id_list = entity_id.split(".")
            if entity_id_list[0] == "sensor":
                sensors.append({"entity_id": entity_id, "name": entity['attributes']["friendly_name"]})
            elif entity_id_list[0] == "switch":
                lamps.append({"entity_id": entity_id, "name": entity['attributes']["friendly_name"]})
        logging.info("Choose your illumination sensor:")
        i = 0
        for line in sensors:
            logging.info(f"{i} - {line['name']}, entyti_id: {line['entity_id']}")
            i += 1
        sensor_number = int(input("Write the number of choosen sensor: "))
        logging.info("Choose your lamp:")
        i = 0
        for line in lamps:
            logging.info(f"{i} - {line['name']}, entyti_id: {line['entity_id']}")
            i += 1
        lamp_number = int(input("Write the number of choosen lamp: "))
        logging.info(f"You have chosen {sensors[sensor_number]} and {lamps[lamp_number]}")
        self.config['sensor_id'] = sensors[sensor_number]['entity_id']
        self.config['light_socket_id'] = lamps[lamp_number]['entity_id']
        with open(f"{self.path}illumination_config.yaml", "w") as f:
            yaml.dump(self.config, f)


    def get_request(self, url: str) -> tp.List[tp.Tuple[str, str]]:
        url = f"http://localhost:8123/api/{url}"
        headers = {
            "Authorization": f"Bearer {self.config['access_token']}",
            "content-type": "application/json",
        }
        logging.debug(f"Get reques to url: {url}")
        response = get(url, headers=headers)
        logging.debug(f"Response for get request {response}")
        assert response.status_code == 200
        text = response.text
        text = text.replace('true', '"true"')
        text = text.replace('false', '"false"')
        text = text.replace('null', '"null"')
        text = literal_eval(text)
        return text

    def control_lamp(self, command: str) -> None:
        url = f"http://localhost:8123/api/services/switch/{command}"
        headers = {
            "Authorization": f"Bearer {self.config['access_token']}",
            "content-type": "application/json",
        }
        logging.debug(f"Sending post request to url {url}")
        data = {"entity_id": self.config['light_socket_id']}
        response = post(url, headers=headers, json=data)
        logging.debug(f"Response for post request {response}")
        assert response.status_code == 200
        logging.info(f"Lamp turned {command[5:]}")

    def calculate_illumination(self, lux: int, delay: int) -> None:
        mkmol_add = lux/float(self.config['lamp_coefficient'])
        mkmol = int(self.data['mkmol'])
        mkmol += mkmol_add*delay
        logging.debug(f"Mkmol after calculation: {mkmol}")
        with open(f"{self.path}data/illumination.yaml", "w") as f:
            self.data['mkmol'] = mkmol
            yaml.dump(self.data, f)

    def spin(self):
        delay = 30
        while True:
            time.sleep(delay)
            state_response = self.get_request(f"states/{self.config['light_socket_id']}")
            self.lamp_state = state_response['state']
            logging.debug(f"Lamp state: {self.lamp_state}")
            if self.lamp_state == "on":
                response = self.get_request(f"states/{self.config['sensor_id']}")
                self.calculate_illumination(lux=int(response['state']), delay=delay)
                if self.data['mkmol'] > int(self.config['dli']):
                    self.control_lamp("turn_off")
            elif self.lamp_state == "off":
                if self.data['mkmol'] < int(self.config['dli']):
                    self.control_lamp("turn_on")
            date = datetime.today()
            if date.day != int(self.data['date']):
                logging.debug(f"New day {date.day}")
                self.data['mkmol'] = 0
                self.data['date'] = date.day
                with open(f"{self.path}data/illumination.yaml", "w") as f:
                    yaml.dump(self.data, f)

                    
if __name__ == '__main__':
    IlluminationAutomation().spin()