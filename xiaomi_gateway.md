# Sensors Connection Method 2 (with Xiaomi Gateway)

You need your Xiaomi gateway along with all the sensors to be connected to the Mi Home app. If you haven't done this yet press `+` button on the top right corner, find your hub (it must be in connecting mode which is achieved via a long press of the power button) and follow instructions in the app. After you add the gateway, you need to add sensors: press on your gateway, then go to `Child device` and press `+`. Find required device and follow the instructions on the screen. For more details refer to the user manual of your Xiaomi Gateway hub.

## Add Gateway to Home Assistant
Be sure that you're logged in you raspberry as `homeassistant` user, if not do the following:
```bash
sudo -u homeassistant -H -s
```

In your Home Assistant:
```
http://<raspberry_address>:8123
```
Go to `Configuration/Integrations` and press `Add Intagration`. There you need to Find `Xiaomi Miio`:

![integration](media/integration.png)

Then fill your username (or phone) and password from Mi Home account and choose your country server:

![auth](media/auth.png)

Press `Submit` and choose your Hub (Aqara Hub in this example):

![hub](media/hub.png)

Press `Submit` and you will be able to see your gateway in Integrations page.

## Add Gateway to Home Assistant using Homekit Controller integration

You can also connect your hub to Aqara Home app on ios and then add it to Home Assistant through Homekit Controller integration. 

Add your hub to the app using `add device` or `+` button. Right after your hub added to Aqara Home app you will be proposed to bind it with your Homekit account. 

![homekit](media/homekit.png)

When you see a menu like the picture, open your Home Assistant page:

```
http://<raspberry_address>:8123
```
Go to `Configuration/Integrations`. Here you can find your device discovered and click `Configure` button to add it by Homekit Controller integration. You have to enter pairing code of your device, which you can find on the sticker on your device.

![configure1](media/configure1.png)

![configure2](media/configure2.png)


## Configuration file

After you've added your devices, you need to add them in a `config.config` file with their seeds. Firstly in `Configuration/Entities` tab in your Home Assistant find entity ids of your devices:

![entity_id](media/entity_id.png)

Open the configuration file:
```bash
nano /srv/homeassistant/python_scripts/config.config
```
And add there information of your devices in the following format:

```
[device_name]
IDS = ['entity_id1', 'entity_id2']
MNEMONIC_SEED = word word word
```
Where `device_name` is the name of your device (you can choose any name), `IDS` are entity ids of the data from the device (it may be one or more ids) and `MNEMONIC_SEED` is a mnemonic seed from robonomics account to this device.

After you fill the configuration file you need to get access token from Home Assistant. For that open your `profile` in the lower left corner:

![profile](media/profile.png)

In the end of the page find `Long-Lived Access Tokens` and press `create token`. Save it somewhere, you will not be able to see it again.

![token](media/token.png)

Now run `create_config.py` script with your token:

```bash
cd /srv/homeassistant
python3 python_scripts/create_config.py --token <access_token>
```
And restart Home Assistant:
```bash
systemctl restart home-assistant@homeassistant.service
```
You can add the data from sensors to your homepage like in `Home Assistant setup` in the description to [Method 1](zigbee2MQTT.md).
