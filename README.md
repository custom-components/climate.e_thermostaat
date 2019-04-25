[![Version](https://img.shields.io/badge/version-0.2.1-green.svg?style=for-the-badge)](#) [![mantained](https://img.shields.io/maintenance/yes/2019.svg?style=for-the-badge)](#)

[![maintainer](https://img.shields.io/badge/maintainer-%20%40gerard33-blue.svg?style=for-the-badge)](#)

# custom_component for Dutch E-thermostaat (ICY)
A platform which allows you to interact with the Dutch E-Thermostaat (ICY).

To get started put `/custom_components/e_thermostaat/climate.py` here:

`<config directory>/custom_components/e_thermostaat/climate.py`  

Starting with Home Assistant 0.92 you also need to copy the file `/custom_components/e_thermostaat/__init__.py` to `<config directory>/custom_components/e_thermostaat/__init__.py`

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
