This repo contains instructions on how to connect your smart home devices to the Robonomics network. You need Robonomics accounts for each device, they will publish encrypted data in datalog. Also you need user account that will send commands to devices end encrypt/decrypt data.

# Home Assistant

Most of smart devices can be connected through Home Assistant.

## Requirements

* Raspberry Pi 4 or 3
* SD card and SD adapter
* Temperature sensor - [Keen Home RS-THP-MP-1.0](https://www.zigbee2mqtt.io/devices/RS-THP-MP-1.0.html) (or another [supported device](https://www.zigbee2mqtt.io/information/supported_devices.html))

### Method 1 (with zigbee2MQTT)
* Zigbee adapter [JetHome USB JetStick Z2](https://jhome.ru/catalog/parts/PCBA/293/) (or one of [supported](https://www.zigbee2mqtt.io/information/supported_adapters.html))

### Method 2 (with Xiaomi Gateway)
* Xiaomi Gateway (one of [supported](https://www.home-assistant.io/integrations/xiaomi_miio#xiaomi-gateway))
* [Mi Home app](https://play.google.com/store/apps/details?id=com.xiaomi.smarthome&hl=ru&gl=US) or HomeKit app

Also you can connect some devices directly through Mi Home app (for example, Vacuum Cleaner).

## Setup

1. First you need to [setup Raspberry Pi](docs/raspberry_setup.md) (also you can [use prepared image](docs/raspberry_image.md)).
2. Then you need to connect devices:
- [Connection with zigbee2MQTT](docs/zigbee2MQTT.md)
- [Connection through Xiaomi Gateway](docs/xiaomi_gateway.md)
- [Connect Vacuum Cleaner](docs/vacuum_connect.md)

# Automations

 - [Illumination](docs/illumination.md)


# Without Home Assistant

It is also possible to connect devices directly to Robonomics. There is an instruction how to get encrypted data from [SDS011 particle sensor](docs/sds_connect.md). 
