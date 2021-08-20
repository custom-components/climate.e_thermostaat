"""
Adds support for the Essent Icy E-Thermostaat units.

For more details about this platform, please refer to the documentation at
https://github.com/custom-components/climate.e_thermostaat
"""
import datetime

import logging

import requests

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.climate.const import (
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    HVAC_MODE_HEAT,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_PASSWORD,
    CONF_USERNAME,
    TEMP_CELSIUS,
)

try:
    from homeassistant.components.climate import (
        ClimateEntity,
        PLATFORM_SCHEMA,
    )
except ImportError:
    from homeassistant.components.climate import (
        ClimateDevice as ClimateEntity,
        PLATFORM_SCHEMA,
    )

__version__ = "0.3.5"

_LOGGER = logging.getLogger(__name__)

URL_LOGIN = "https://portal.icy.nl/login"
URL_DATA = "https://portal.icy.nl/data"

DEFAULT_NAME = "E-Thermostaat"

CONF_NAME = "name"
CONF_COMFORT_TEMPERATURE = "comfort_temperature"
CONF_SAVING_TEMPERATURE = "saving_temperature"
CONF_AWAY_TEMPERATURE = "away_temperature"

STATE_COMFORT = "Comfortstand"  # "comfort"
STATE_SAVING = "Bespaarstand"  # "saving"
STATE_AWAY = "Lang-weg-stand"  # "away"
STATE_FIXED_TEMP = "Vaste temperatuur"  # "fixed temperature"

DEFAULT_COMFORT_TEMPERATURE = 20
DEFAULT_SAVING_TEMPERATURE = 17
DEFAULT_AWAY_TEMPERATURE = 12

# Values from web interface
MIN_TEMP = 10
MAX_TEMP = 25

# Values of E-Thermostaat to map to operation mode
COMFORT = 32
SAVING = 64
AWAY = 0
FIXED_TEMP = 128

SUPPORT_FLAGS = SUPPORT_PRESET_MODE | SUPPORT_TARGET_TEMPERATURE
SUPPORT_PRESET = [STATE_AWAY, STATE_COMFORT, STATE_FIXED_TEMP, STATE_SAVING]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(
            CONF_AWAY_TEMPERATURE, default=DEFAULT_AWAY_TEMPERATURE
        ): vol.Coerce(float),
        vol.Optional(
            CONF_SAVING_TEMPERATURE, default=DEFAULT_SAVING_TEMPERATURE
        ): vol.Coerce(float),
        vol.Optional(
            CONF_COMFORT_TEMPERATURE, default=DEFAULT_COMFORT_TEMPERATURE
        ): vol.Coerce(float),
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the E-Thermostaat platform."""
    name = config.get(CONF_NAME)
    comfort_temp = config.get(CONF_COMFORT_TEMPERATURE)
    saving_temp = config.get(CONF_SAVING_TEMPERATURE)
    away_temp = config.get(CONF_AWAY_TEMPERATURE)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    add_entities(
        [EThermostaat(name, username, password, comfort_temp, saving_temp, away_temp)]
    )


class EThermostaat(ClimateEntity):
    """Representation of a E-Thermostaat device."""

    def __init__(self, name, username, password, comfort_temp, saving_temp, away_temp):
        """Initialize the thermostat."""
        self._name = name
        self._username = username
        self._password = password

        self._comfort_temp = comfort_temp
        self._saving_temp = saving_temp
        self._away_temp = away_temp

        self._current_temperature = None
        self._target_temperature = None
        self._last_seen = None
        self._old_conf = None
        self._current_operation_mode = None

        self._uid = None
        self._token = None

        self.update()

    @property
    def name(self):
        """Return the name of the thermostat."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this thermostat."""
        return "_".join([self._name, "climate"])

    @property
    def should_poll(self):
        """Return if polling is required."""
        return True

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return MIN_TEMP

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return MAX_TEMP

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._last_seen and datetime.datetime.now() - self._last_seen < datetime.timedelta(seconds=600)

    @property
    def hvac_mode(self):
        """Return hvac operation ie. heat, cool mode."""
        return HVAC_MODE_HEAT

    @property
    def hvac_modes(self):
        """HVAC modes."""
        return [HVAC_MODE_HEAT]

    @property
    def hvac_action(self):
        """Return the current running hvac operation."""
        if self._target_temperature < self._current_temperature:
            return CURRENT_HVAC_IDLE
        return CURRENT_HVAC_HEAT

    @property
    def preset_mode(self):
        """Return the current preset mode, e.g., home, away, temp."""
        return self._current_operation_mode

    @property
    def preset_modes(self):
        """Return a list of available preset modes."""
        return SUPPORT_PRESET

    @property
    def is_away_mode_on(self):
        """Return true if away mode is on."""
        return self._current_operation_mode in [STATE_AWAY]

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    def set_preset_mode(self, preset_mode: str):
        """Set new preset mode."""
        if preset_mode == STATE_COMFORT:
            self._set_temperature(self._comfort_temp, mode_int=COMFORT)
        elif preset_mode == STATE_SAVING:
            self._set_temperature(self._saving_temp, mode_int=SAVING)
        elif preset_mode == STATE_AWAY:
            self._set_temperature(self._away_temp, mode_int=AWAY)
        elif preset_mode == STATE_FIXED_TEMP:
            self._set_temperature(self._target_temperature, mode_int=FIXED_TEMP)

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        self._set_temperature(temperature)

    def _set_temperature(self, temperature, mode_int=None):
        """Set new target temperature, via URL commands."""
        payload_new = [("temperature1", temperature)]

        if self._old_conf is not None:
            # overwrite first int to set mode
            if mode_int is not None:
                payload_new.append(("configuration[]", mode_int))
            elif (
                self._current_operation_mode
                and self._current_operation_mode == STATE_FIXED_TEMP
            ):
                payload_new.append(("configuration[]", FIXED_TEMP))
            else:
                payload_new.append(("configuration[]", COMFORT))
            mode_int = payload_new[1][1]
            # append old config not to overwrite old settings
            for i in self._old_conf[1:]:
                payload_new.append(("configuration[]", i))

        if self._request_with_retry(URL_DATA, payload_new, request_type="post"):
            # update state values since we assume update was successful
            self._current_operation_mode = self.map_int_to_operation_mode(mode_int)
            self._target_temperature = temperature
            # self.schedule_update_ha_state(force_refresh=True)

    def get_token_and_uid(self):
        """Get the Session Token and UID of the Thermostaat."""
        payload = {"username": self._username, "password": self._password}
        with requests.Session() as s:
            try:
                s.get(URL_LOGIN)
                r = s.post(URL_LOGIN, data=payload)
                res = r.json()
                self._token = res["token"]
                self._uid = res["serialthermostat1"]
            except Exception as e:
                _LOGGER.error("Could not get token and uid: %s" % e)

    def _send_request_with_header(self, url, payload, request_type):
        """Send the request with header and set the uid if necessary."""
        header = {"Session-token": self._token}
        if request_type == "get":
            # for get data just use payload as is
            payload_new = payload
            req_func = requests.get
        else:
            # make a local copy to prevent overwriting
            payload_new = [x for x in payload]
            payload_new.append(("uid", self._uid))
            req_func = requests.post
        try:
            r = req_func(url, data=payload_new, headers=header)
            return r
        except Exception as e:
            _LOGGER.error("Could not connect to E-Thermostaat." "error: %s" % e)

    def _request_with_retry(self, url, payload, request_type):
        """Try once with old token, if fails get new token and try again."""
        if self._uid is None or self._token is None:
            self.get_token_and_uid()
        r = self._send_request_with_header(url, payload, request_type)

        # if unauthorized, get new token and uid
        if r is None or r.json()["status"]["code"] == 401:
            self.get_token_and_uid()
            r = self._send_request_with_header(url, payload, request_type)
        # Code 200 is success
        if r is None or not r.json()["status"]["code"] == 200:
            _LOGGER.error("Could not set temperature, " "error on the server side")
        return r

    def _get_data(self):
        """Get the data of the E-Thermostaat."""
        payload = (("username", self._username), ("password", self._password))

        r = self._request_with_retry(URL_DATA, payload, request_type="get")
        if r:
            data = r.json()

            self._target_temperature = data["temperature1"]
            self._current_temperature = data["temperature2"]
            
            self._last_seen = datetime.datetime.strptime(data["last-seen"], '%Y-%m-%d %H:%M:%S')

            self._old_conf = data["configuration"]
            self._current_operation_mode = self.map_int_to_operation_mode(
                self._old_conf[0]
            )
            _LOGGER.debug("E-Thermostaat value: {}".format(self._old_conf[0]))
        else:
            _LOGGER.error("Could not get data from E-Thermostaat.")

    def update(self):
        """Get the latest data."""
        self._get_data()

    @staticmethod
    def map_int_to_operation_mode(config_int):
        """Map the value of the E-Thermostaat to the operation mode."""
        if AWAY <= config_int < COMFORT:
            return STATE_AWAY
        elif COMFORT <= config_int < SAVING:
            return STATE_COMFORT
        elif SAVING <= config_int < FIXED_TEMP:
            return STATE_SAVING
        return STATE_FIXED_TEMP
