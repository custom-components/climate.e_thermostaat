{% if installed %}
### Thanks for using this custom component.

{% endif %}

{% if prerelease %}
### This is a Beta version!

{% endif %}

{% if installed and version_installed < "0.3.0" %}
### Version 0.3.0 and later of this component only work on HA 0.96 and later. If you are on an older version of HA use [release 0.2.3](https://github.com/custom-components/climate.e_thermostaat/releases/tag/0.2.3) of this component.

{% endif %}

[![Version](https://img.shields.io/badge/version-0.3.0-green.svg?style=for-the-badge)](#)
[![mantained](https://img.shields.io/maintenance/yes/2019.svg?style=for-the-badge)](#)
[![maintainer](https://img.shields.io/badge/maintainer-%20%40gerard33-blue.svg?style=for-the-badge)](#)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
[![Community Forum](https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge)](https://community.home-assistant.io/t/e-thermostaat-icy/493?u=gerard33)

# Custom component for Dutch E-thermostaat (ICY)
A platform which allows you to interact with the Dutch E-Thermostaat (ICY).

## Screenshot
_ICY E-Thermostaat_

![ICY E-Thermostaat](https://github.com/custom-components/climate.e_thermostaat/blob/master/screenshots/e_thermostaat.jpg)

## Configuration
**Example configuration.yaml:**

```yaml
climate:
  - platform: e_thermostaat
    username: !secret icy_user
    password: !secret icy_pass
    comfort_temperature: 20
    saving_temperature: 17
    away_temperature: 12
```

**Configuration variables:**  
  
key | description  
:--- | :---  
**platform (Required)** | The platform name.
**username (Required)** | The username of your E-Thermostaat account.
**password (Required)** | The password of your E-Thermostaat account.
**comfort_temperature (Optional)** | The comfort temperature (Comfortstand), defaults to 20.  
**saving_temperature (Optional)** | The saving temperature (Bespaarstand), defaults to 17.  
**away_temperature (Optional)** | The away temperature (Lang-weg-stand), defaults to 12.  


This platform is using the [E-Thermostaat API](https://www.e-thermostaat.nl/) to get the information from the thermostat.
This component is only usefull for Dutch users as the E-Thermostaat is only sold in The Netherlands.
