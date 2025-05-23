# fressnapf_tracker

[![License][license-shield]](LICENSE.md)


> [!IMPORTANT]
> This component is a private development and not connected to Fressnapf in any way.

_Homeassistant Custom Component for [Fressnapf Tracker](https://tracker.fressnapf.de/)._

![example][exampleimg]

## Installation

### HACS

The easiest way to add this to your Homeassistant installation is using [HACS](https://hacs.xyz/):

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?repository=hass-fressnapf-tracker&owner=k0ssi&category=integration)

### Manual

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `fressnapf_tracker`.
4. Download _all_ the files from the `custom_components/fressnapf_tracker/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant

## Configuration

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=fressnapf_tracker)

### Manual
In the HA UI go to `Configuration` -> `Integrations` click `+` and search for `Fressnapf Tracker`


---



[exampleimg]: https://github.com/eifinger/hass-fressnapf-tracker/blob/main/docs/images/example.png?raw=true
[license-shield]: https://img.shields.io/github/license/eifinger/hass-fressnapf-tracker.svg?style=for-the-badge
