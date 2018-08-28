# custom_component for Dutch E-thermostaat (ICY)
A platform which allows you to interact with the Dutch E-Thermostaat (ICY).

To get started put `/custom_components/climate/e_thermostaat.py` here:

`<config directory>/custom_components/climate/e_thermostaat.py`  
  
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
  
***
Due to how `custom_componentes` are loaded, it is normal to see a `ModuleNotFoundError` error on first boot after adding this, to resolve it, restart Home-Assistant.

***
