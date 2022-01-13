# Connect SDS particular sensor to robonomics

## Requirements
- particle sensor SDS011 with USB connector

## Installation
Install python packages:
```bash
pip3 install pynacl packaging pycurl
pip3 install substrate-interface==1.1.2
```
Also you need to get access to the USB port adding your user to dialout group:
```bash
sudo usermod -a -G dialout $USER
```
Then logout and login or restart the computer.

And clone the repository:
```bash
git clone https://github.com/airalab/robonomics-smarthome.git
```

## Configuration

Create file `config.config` in `python_scripts` directory:
```bash
nano python_scripts/config.config
```
And add there information about your accounts:
```
[user]
SEED = <raw_or_mnemonic_seed_from_your_user_account>
[SDS]
IDS=['PM25', 'PM10']
SEED = <raw_or_mnemonic_seed_from_your_sensor_account>
```
In the `config_sds.py` file you can specify the name of your USB port (default `/dev/ttyUSB0`) and how often sensor will send data (`work_period`).

## Run

Connect sensor via USB connector to the computer and run script `run_sds.py`:
```bash
python3 python_scripts/run_sds.py
```
You will be able to see your encrypted data in sensors's account datalog in [subscan](https://robonomics.subscan.io/). You can decrypt it with `decrypt.py` script:
```bash
python3 python_scripts/decrypt.py <encrypted_data>
```