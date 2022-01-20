# Connect SDS particular sensor to robonomics

## Requirements

- particle sensor SDS011 Nodemcu V3 connected with [this instruction](https://wiki.robonomics.network/docs/en/connect-sensor-to-robonomics/)

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
And add there information about your user account:
```
[user]
SEED = <raw_or_mnemonic_seed_from_your_user_account>
[SDS]
IDS=['PM10', 'PM2.5', 'CO2', 'TVOC', 'Temperature', 'Humidity']
SEED = 
```
In `IDS` write names of all your sensors data. It must match the names in ESP logs (you can find it in `debug level` page in your sensor web interface).

## Run

Connect ESP via USB to the computer and run script `run_sds.py`:
```bash
python3 python_scripts/run_sds.py
```
If you didn't write seed for SDS in config, it will be automatically created and you will see public address in terminal (seed will be added to the config). To start publish encrypted data to Robonomics you need XRT in you sensor account and `launch` transaction to it. With launch transactions you can stop and start sending data to Robonomics.

You will be able to see your encrypted data in sensors's account datalog in [subscan](https://robonomics.subscan.io/). You can decrypt it with `decrypt.py` script:
```bash
python3 python_scripts/decrypt.py <encrypted_data>
```