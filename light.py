"""Philips Hue BLE light implementation"""

from __future__ import annotations

import logging

from .hue import HueLightInstance
import voluptuous as vol

from pprint import pformat

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (SUPPORT_BRIGHTNESS, ATTR_BRIGHTNESS,
                                            PLATFORM_SCHEMA, LightEntity)
from homeassistant.const import CONF_NAME, CONF_MAC
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger("hue_ble")

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME): cv.string,
    vol.Required(CONF_MAC): cv.string,
})


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the Hue Light platform."""
    # Add devices
    _LOGGER.info(pformat(config))
    
    light = {
        "name": config[CONF_NAME],
        "mac": config[CONF_MAC]
    }
    
    add_entities([HueLight(light)])

class HueLight(LightEntity):
    """Representation of a Hue Light."""

    def __init__(self, light) -> None:
        """Initialize an AwesomeLight."""
        _LOGGER.info(pformat(light))
        self._light = HueLightInstance(light["mac"])
        self._name = light["name"]
        self._state = None
        self._brightness = None

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def supported_features(self):
        return SUPPORT_BRIGHTNESS

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """

        if ATTR_BRIGHTNESS in kwargs:
            await self._light.set_brightness(kwargs.get(ATTR_BRIGHTNESS, 255))

        await self._light.turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self._light.turn_off()

    async def async_update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = await self._light.is_on()
        self._brightness = await self._light.get_brightness()
