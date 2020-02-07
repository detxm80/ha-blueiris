"""
Support for Blue Iris binary sensors.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/binary_sensor.blueiris/
"""
import logging

from homeassistant.helpers.dispatcher import async_dispatcher_connect

from custom_components.blueiris.binary_sensors.audio import BlueIrisAudioBinarySensor
from custom_components.blueiris.binary_sensors.motion import BlueIrisMotionBinarySensor
from .const import *
from custom_components.blueiris.binary_sensors.main import BlueIrisMainBinarySensor, ALL_BINARY_SENSORS
from custom_components.blueiris.binary_sensors.connectivity import BlueIrisConnectivityBinarySensor

from .blue_iris_api import _get_api

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = [DOMAIN, 'mqtt']


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up the BlueIris Switch."""
    _LOGGER.debug(f"Starting async_setup_entry")

    api = _get_api(hass)

    if api is None:
        return

    main_binary_sensor = BlueIrisMainBinarySensor()

    camera_list = api.camera_list

    entities = []
    for camera in camera_list:
        _LOGGER.debug(f"Processing new binary sensor: {camera}")

        camera_id = camera.get("optionValue")
        audio_support = camera.get("audio", False)
        is_system = camera_id in SYSTEM_CAMERA_ID

        allowed_binary_sensors = []

        if not is_system:
            allowed_binary_sensors.append(BlueIrisMotionBinarySensor)

            if audio_support:
                allowed_binary_sensors.append(BlueIrisAudioBinarySensor)

        allowed_binary_sensors.append(BlueIrisConnectivityBinarySensor)

        for binary_sensor in allowed_binary_sensors:
            entity = binary_sensor(camera)

            main_binary_sensor.register(entity)

            entities.append(entity)

    entities.append(main_binary_sensor)

    binary_sensors = main_binary_sensor.get_binary_sensors()
    _LOGGER.info(f"Registered binary sensors: {binary_sensors}")

    async_add_devices(entities)
