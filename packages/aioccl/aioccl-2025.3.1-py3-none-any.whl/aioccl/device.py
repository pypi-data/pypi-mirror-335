"""CCL device mapping."""

from __future__ import annotations

import logging
import time
from typing import Callable, TypedDict

from .sensor import CCLSensor, CCL_SENSORS

_LOGGER = logging.getLogger(__name__)

CCL_DEVICE_INFO_TYPES = ("serial_no", "mac_address", "model", "fw_ver")


class CCLDevice:
    """Mapping for a CCL device."""

    def __init__(self, passkey: str):
        """Initialize a CCL device."""

        class Info(TypedDict):
            """Store device information."""
            fw_ver: str | None
            last_update_time: float | None
            mac_address: str | None
            model: str | None
            passkey: str
            serial_no: str | None

        self._info: Info = {
            "fw_ver": None,
            "last_update_time": None,
            "mac_address": None,
            "model": None,
            "passkey": passkey,
            "serial_no": None,
        }

        self._binary_sensors: dict[str, CCLSensor] | None = {}
        self._sensors: dict[str, CCLSensor] | None = {}
        self._update_callbacks = {}

        self._new_binary_sensor_callbacks = set()
        self._new_sensors: list[CCLSensor] | None = []
        self._new_sensor_callbacks = set()

    @property
    def passkey(self) -> str:
        """Return the passkey."""
        return self._info["passkey"]

    @property
    def device_id(self) -> str | None:
        """Return the device ID."""
        if self.mac_address is None:
            return None
        return self.mac_address.replace(":", "").lower()[-6:]

    @property
    def last_update_time(self) -> str | None:
        """Return the last update time."""
        return self._info["last_update_time"]

    @property
    def name(self) -> str | None:
        """Return the display name."""
        if self.device_id is not None:
            return self.model + " - " + self.device_id
        return self._info["model"]

    @property
    def mac_address(self) -> str | None:
        """Return the MAC address."""
        return self._info["mac_address"]

    @property
    def model(self) -> str | None:
        """Return the model."""
        return self._info["model"]

    @property
    def fw_ver(self) -> str | None:
        """Return the firmware version."""
        return self._info["fw_ver"]

    @property
    def binary_sensors(self) -> dict[str, CCLSensor] | None:
        """Store binary sensor data under this device."""
        return self._binary_sensors

    @property
    def sensors(self) -> dict[str, CCLSensor] | None:
        """Store sensor data under this device."""
        return self._sensors

    def update_info(self, new_info: dict[str, None | str]) -> None:
        """Add or update device info."""
        for key, value in new_info.items():
            if key in self._info:
                self._info[key] = str(value)
        self._info["last_update_time"] = time.monotonic()

    def update_sensors(self, sensors: dict[str, None | str | int | float]) -> None:
        """Add or update all sensor values."""
        for key, value in sensors.items():
            if CCL_SENSORS.get(key).binary:
                if key not in self.binary_sensors:
                    self._binary_sensors[key] = CCLSensor(key)
                    self._new_sensors.append(self.binary_sensors[key])
                self._binary_sensors[key].value = value
            else:
                if key not in self.sensors:
                    self._sensors[key] = CCLSensor(key)
                    self._new_sensors.append(self.sensors[key])
                self._sensors[key].value = value

        add_count = self._publish_new_sensors()
        _LOGGER.debug(
            "Added %s new sensors for device %s at %s.",
            add_count,
            self.device_id,
            self.last_update_time,
        )

        update_count = self._publish_updates()
        _LOGGER.debug(
            "Updated %s sensors in total for device %s at %s.",
            update_count,
            self.device_id,
            self.last_update_time,
        )

    def register_update_cb(self, sensor_key, callback: Callable[[], None]) -> None:
        """Register callback, called when Sensor changes state."""
        self._update_callbacks[sensor_key] = callback

    def remove_update_cb(self, sensor_key, callback: Callable[[], None]) -> None:
        """Remove previously registered callback."""
        self._update_callbacks.pop(sensor_key, None)

    def _publish_updates(self) -> int:
        """Schedule call all registered callbacks."""
        count = 0
        for sensor_key, callback in self._update_callbacks.items():
            try:
                callback()
                count += 1
            except Exception as err:  # pylint: disable=broad-exception-caught
                _LOGGER.warning(
                    "Error while updating sensor %s for device %s: %s",
                    sensor_key,
                    self.device_id,
                    err,
                )
        return count

    def register_new_binary_sensor_cb(self, callback: Callable[[], None]) -> None:
        """Register callback, called when Sensor changes state."""
        self._new_binary_sensor_callbacks.add(callback)

    def remove_new_binary_sensor_cb(self, callback: Callable[[], None]) -> None:
        """Remove previously registered callback."""
        self._new_binary_sensor_callbacks.discard(callback)

    def register_new_sensor_cb(self, callback: Callable[[], None]) -> None:
        """Register callback, called when Sensor changes state."""
        self._new_sensor_callbacks.add(callback)

    def remove_new_sensor_cb(self, callback: Callable[[], None]) -> None:
        """Remove previously registered callback."""
        self._new_sensor_callbacks.discard(callback)

    def _publish_new_sensors(self) -> None:
        """Schedule call all registered callbacks."""
        count = 0
        for sensor in self._new_sensors[:]:
            try:
                if sensor.binary:
                    for callback in self._new_binary_sensor_callbacks:
                        callback(sensor)
                else:
                    for callback in self._new_sensor_callbacks:
                        callback(sensor)
                self._new_sensors.remove(sensor)
                count += 1
            except Exception as err:  # pylint: disable=broad-exception-caught
                _LOGGER.warning(
                    "Error while adding sensor %s for device %s: %s",
                    sensor.key,
                    self.device_id,
                    err,
                )
        return count
