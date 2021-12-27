from requests import get
from ast import literal_eval
import yaml
from utils import read_config
import argparse

light_fields = ['rgb_color', 'brightness', 'effect']
start_text = """
default_config:

tts:
  - platform: google_translate
group: !include groups.yaml
script: !include scripts.yaml
scene: !include scenes.yaml

"""
light_parameters = ['brightness', 'rgb_color', 'effect']

def write_config_start(config, filename, start_text):
    with open(filename, "w") as f:
        f.write(start_text)
    if 'automation' not in config:
        config['automation'] = []
    if 'shell_command' not in config:
        config['shell_command'] = {}
    return config

def write_config_automation(config, ids, services):
    print(ids)
    for device in ids:
        print(ids[device])
        entities = literal_eval(ids[device])
        entity_id = entities[0]
        entity_name = device
        entity_domain = entity_id.split('.')[0]
        send_datalog_automation_state = {'alias': f'send_datalog_{entity_name}', 
                'trigger': {'platform': 'state', 'entity_id': [entity_id]}, 
                'action': {'service': f'shell_command.send_datalog_{entity_name}'}}
        config['automation'].append(send_datalog_automation_state)
        send_datalog_automation_time = {'alias': f'send_datalog_{entity_name}', 
                'trigger': {'platform': 'time_pattern', 'minutes': '/1'}, 
                'action': {'service': f'shell_command.send_datalog_{entity_name}'}}
        config['automation'].append(send_datalog_automation_time)
        data = f'{device} '
        for entity in entities:
            data += f'{entity}:{{{{ states("{entity}") }}}} '
        data = data[:-1]
        config['shell_command'][f'send_datalog_{entity_name}'] = f'python3 python_scripts/send_datalog.py {data}'

        for domain in services:
            print(f"domain: {domain['domain']}")
            if domain['domain'] == entity_domain:
                for service in domain['services']:
                    print(f"service {service}")
                    if (domain['domain'] == 'light') and (service == 'turn_on'):
                        for parameter in light_parameters:
                            if parameter == 'rgb_color':
                                parameter_data = '[{{ trigger.json.r }}, {{ trigger.json.g }}, {{ trigger.json.b }}]'
                            else:
                                parameter_data = f'{{{{ trigger.json.{parameter} }}}}'
                            control_automation = {'alias': f'{entity_name}_{service}_{parameter}', 
                                        'trigger': {'platform': 'webhook', 'webhook_id': f'{entity_name}_{service}_{parameter}'}, 
                                        'action': {'service': f'{domain["domain"]}.{service}', 'target': {'entity_id': [entity_id]}, 'data': {f'{parameter}': parameter_data}}}
                            config['automation'].append(control_automation)
                    control_automation = {'alias': f'{entity_name}_{service}', 
                                        'trigger': {'platform': 'webhook', 'webhook_id': f'{entity_name}_{service}'}, 
                                        'action': {'service': f'{domain["domain"]}.{service}', 'target': {'entity_id': [entity_id]}}}
                    config['automation'].append(control_automation)
    return config

def get_entities(address:str, token:str) -> dict:
    """
    Create a request to Home Assistant to get list of entities

    Parameters
    ----------
    address: str
        Home Assistant address
    token: str
        Access token from Home Assistant

    Returns
    -------
    entities: dict
        Dictionary with all entities and its description
    """

    url = f"http://{address}:8123/api/states"
    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    }

    response = get(url, headers=headers)
    text = response.text
    text = text.replace('true', '"true"')
    text = text.replace('false', '"false"')
    text = text.replace('null', '"null"')
    text = literal_eval(text)
    return text

def get_services(address:str, token:str) -> dict:
    """
    Create a request to Home Assistant to get list of services

    Parameters
    ----------
    address: str
        Home Assistant address
    token: str
        Access token from Home Assistant

    Returns
    -------
    entities: dict
        Dictionary with all services and its description
    """

    url = f"http://{address}:8123/api/services"
    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    }

    response = get(url, headers=headers)
    text = response.text
    text = text.replace('true', '"true"')
    text = text.replace('false', '"false"')
    text = text.replace('null', '"null"')
    text = literal_eval(text)
    return text

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", type=str, 
                        help="Access token from Home Assistant")
    parser.add_argument("--address", type=str, default="localhost", 
                        help="Home Assistant address")
    parser.add_argument("--path", default="/home/homeassistant/.homeassistant/configuration.yaml", 
                        help="Path to create configuration file")
    args = parser.parse_args()
    token = args.token
    address = args.address
    filename = args.path
    entities = get_entities(address, token)
    services = get_services(address, token)
    config, ids = read_config('python_scripts/config.config')
    try:
        with open(filename, "r") as stream:
            config_file = yaml.safe_load(stream)
    except:
        config_file = {}
    config_file = write_config_start(config_file, filename, start_text)
    write_config_automation(config_file, ids, services)
    with open(filename, "a") as f:
        yaml.dump(config_file, f)



