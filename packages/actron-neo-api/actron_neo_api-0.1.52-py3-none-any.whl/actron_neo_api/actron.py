import aiohttp
from .exceptions import ActronNeoAuthError, ActronNeoAPIError

import re

import logging

_LOGGER = logging.getLogger(__name__)


class ActronNeoAPI:
    def __init__(
        self,
        username: str = None,
        password: str = None,
        pairing_token: str = None,
        base_url: str = "https://nimbus.actronair.com.au",
    ):
        """
        Initialize the ActronNeoAPI client.

        Args:
            username (str): Username for Actron Neo account.
            password (str): Password for Actron Neo account.
            pairing_token (str): Pre-existing pairing token for API authentication.
            base_url (str): Base URL for the Actron Neo API.
        """
        self.username = username
        self.password = password
        self.pairing_token = pairing_token
        self.base_url = base_url
        self.access_token = None
        self.status = None
        self.latest_event_id = None
        self.systems = None

        # Validate initialization parameters
        if not self.pairing_token and (not self.username or not self.password):
            raise ValueError(
                "Either pairing_token, or username/password must be provided."
            )

    async def request_pairing_token(
        self, device_name: str, device_unique_id: str, client: str = "ios"
    ):
        """
        Request a pairing token using the user's credentials and device details.
        """
        url = f"{self.base_url}/api/v0/client/user-devices"
        payload = {
            "username": self.username,
            "password": self.password,
            "client": client,
            "deviceName": device_name,
            "deviceUniqueIdentifier": device_unique_id,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    pairing_token = data.get("pairingToken")
                    if not pairing_token:
                        raise ActronNeoAuthError(
                            "Pairing token missing in response.")
                    self.pairing_token = pairing_token
                else:
                    raise ActronNeoAuthError(
                        f"Failed to request pairing token. Status: {response.status}, Response: {await response.text()}"
                    )

    async def refresh_token(self):
        """
        Refresh the access token using the pairing token.
        """
        if not self.pairing_token:
            raise ActronNeoAuthError(
                "Pairing token is required to refresh the access token."
            )

        url = f"{self.base_url}/api/v0/oauth/token"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.pairing_token,
            "client_id": "app",
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data.get("access_token")
                    if not self.access_token:
                        raise ActronNeoAuthError(
                            "Access token missing in response.")
                    self.systems = await self.get_ac_systems()
                    # Initial full status update
                    await self.update_status()
                    # Merge incrementals since full status update
                    await self.update_status()
                else:
                    raise ActronNeoAuthError(
                        f"Failed to refresh access token. Status: {response.status}, Response: {await response.text()}"
                    )

    async def _handle_request(self, request_func, *args, **kwargs):
        """
        Handle API requests, retrying if the token is expired.
        """
        try:
            return await request_func(*args, **kwargs)
        except ActronNeoAuthError as e:
            # Detect token expiration or invalidation based on the error message
            if "invalid_token" in str(e).lower() or "token_expired" in str(e).lower():
                _LOGGER.warning(
                    "Access token expired or invalid. Attempting to refresh."
                )
                await self.refresh_token()
                # Retry the request with the refreshed token
                return await request_func(*args, **kwargs)
            raise  # Re-raise other authorization errors
        except aiohttp.ClientResponseError as e:
            if e.status == 401:  # HTTP 401 Unauthorized
                _LOGGER.warning(
                    "Access token expired (401 Unauthorized). Refreshing token."
                )
                await self.refresh_token()
                return await request_func(*args, **kwargs)
            raise  # Re-raise other HTTP errors

    async def get_ac_systems(self):
        """
        Retrieve all AC systems in the customer account.
        """
        return await self._handle_request(self._get_ac_systems)

    async def _get_ac_systems(self):
        """Internal method to perform the actual API call."""
        if not self.access_token:
            raise ActronNeoAuthError(
                "Authentication required before fetching AC systems."
            )

        url = f"{self.base_url}/api/v0/client/ac-systems?includeNeo=true"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    systems = await response.json()
                    return systems["_embedded"]["ac-system"]
                else:
                    raise ActronNeoAPIError(
                        f"Failed to fetch AC systems. Status: {response.status}, Response: {await response.text()}"
                    )

    async def get_ac_status(self, serial_number: str):
        """
        Retrieve the full status of a specific AC system by serial number.
        """
        return await self._handle_request(self._get_ac_status, serial_number)

    async def _get_ac_status(self, serial_number: str):
        """
        Retrieve the full status of a specific AC system by serial number.
        """
        if not self.access_token:
            raise ActronNeoAuthError(
                "Authentication required before fetching AC system status."
            )

        url = f"{self.base_url}/api/v0/client/ac-systems/status/latest?serial={serial_number}"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    status = await response.json()
                    return status  # Full status of the AC system
                else:
                    raise ActronNeoAPIError(
                        f"Failed to fetch status for AC system {serial_number}. Status: {response.status}, Response: {await response.text()}"
                    )

    async def get_ac_events(
        self, serial_number: str, event_type: str = "latest", event_id: str = None
    ):
        """
        Retrieve events for a specific AC system.

        :param serial_number: Serial number of the AC system.
        :param event_type: 'latest', 'newer', or 'older' for the event query type.
        :param event_id: The event ID for 'newer' or 'older' event queries.
        """
        return await self._handle_request(
            self._get_ac_events, serial_number, event_type, event_id
        )

    async def _get_ac_events(
        self, serial_number: str, event_type: str = "latest", event_id: str = None
    ):
        """
        Retrieve events for a specific AC system.

        :param serial_number: Serial number of the AC system.
        :param event_type: 'latest', 'newer', or 'older' for the event query type.
        :param event_id: The event ID for 'newer' or 'older' event queries.
        """
        if not self.access_token:
            raise ActronNeoAuthError(
                "Authentication required before fetching AC system events."
            )

        if event_type == "latest":
            url = f"{self.base_url}/api/v0/client/ac-systems/events/latest?serial={serial_number}"
        elif event_type == "newer" and event_id:
            url = f"{self.base_url}/api/v0/client/ac-systems/events/newer?serial={serial_number}&newerThanEventId={event_id}"
        elif event_type == "older" and event_id:
            url = f"{self.base_url}/api/v0/client/ac-systems/events/older?serial={serial_number}&olderThanEventId={event_id}"
        else:
            raise ValueError(
                "Invalid event_type or missing event_id for 'newer'/'older' event queries."
            )

        headers = {"Authorization": f"Bearer {self.access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    events = await response.json()
                    return events  # Events of the AC system
                else:
                    raise ActronNeoAPIError(
                        f"Failed to fetch events for AC system {serial_number}. Status: {response.status}, Response: {await response.text()}"
                    )

    async def get_user(self):
        """
        Get user data from the API.
        """
        return await self._handle_request(
            self._get_user
        )

    async def _get_user(self):
        """
        Get user data from the API.
        """
        if not self.access_token:
            raise ActronNeoAuthError(
                "Authentication required before fetching AC system events."
            )

        url = f"{self.base_url}/api/v0/client/account"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    user = await response.json()
                    return user
                else:
                    raise ActronNeoAPIError(
                        f"Failed to fetch user data. Status: {response.status}, Response: {await response.text()}"
                    )

    async def send_command(self, serial_number: str, command: dict):
        """
        Send a command to the specified AC system.

        :param serial_number: Serial number of the AC system.
        :param command: Dictionary containing the command details.
        """
        return await self._handle_request(self._send_command, serial_number, command)

    async def _send_command(self, serial_number: str, command: dict):
        """
        Send a command to the specified AC system.

        :param serial_number: Serial number of the AC system.
        :param command: Dictionary containing the command details.
        """
        if not self.access_token:
            raise ActronNeoAuthError(
                "Authentication required before sending commands.")

        url = (
            f"{self.base_url}/api/v0/client/ac-systems/cmds/send?serial={serial_number}"
        )
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=command, headers=headers) as response:
                if response.status == 200:
                    return await response.json()  # Success response
                else:
                    raise ActronNeoAPIError(
                        f"Failed to send command. Status: {response.status}, Response: {await response.text()}"
                    )

    async def set_system_mode(self, serial_number: str, is_on: bool, mode: str = None):
        """
        Convenience method to set the AC system mode.

        :param serial_number: Serial number of the AC system.
        :param is_on: Boolean to turn the system on or off.
        :param mode: Mode to set when the system is on. Options are: 'AUTO', 'COOL', 'FAN', 'HEAT'. Default is None.
        """
        return await self._handle_request(
            self._set_system_mode, serial_number, is_on, mode
        )

    async def _set_system_mode(self, serial_number: str, is_on: bool, mode: str = None):
        """
        Convenience method to set the AC system mode.

        :param serial_number: Serial number of the AC system.
        :param is_on: Boolean to turn the system on or off.
        :param mode: Mode to set when the system is on. Options are: 'AUTO', 'COOL', 'FAN', 'HEAT'. Default is None.
        """
        command = {
            "command": {
                "UserAirconSettings.isOn": is_on,
                "type": "set-settings"
            }
        }

        if is_on and mode:
            command["command"]["UserAirconSettings.Mode"] = mode

        response = await self.send_command(serial_number, command)
        return response

    async def get_master_model(self, serial_number: str):
        """
        Retrieve the master wall controller serial number.
        """
        return await self._handle_request(self._get_master_model, serial_number)

    async def _get_master_model(self, serial_number: str) -> str | None:
        """Fetch the Master WC Model for the specified AC system."""
        status = await self.get_ac_status(serial_number)
        return (
            status.get("lastKnownState", {})
            .get("AirconSystem", {})
            .get("MasterWCModel")
        )

    async def get_master_serial(self, serial_number: str):
        """
        Retrieve the master wall controller serial number.
        """
        return await self._handle_request(self._get_master_serial, serial_number)

    async def _get_master_serial(self, serial_number: str):
        """
        Retrieve the master wall controller serial number.
        """
        status = await self.get_ac_status(serial_number)
        return (
            status.get("lastKnownState", {}).get(
                "AirconSystem", {}).get("MasterSerial")
        )

    async def get_master_firmware(self, serial_number: str):
        """
        Retrieve the master wall controller firmware version.
        """
        return await self._handle_request(self._get_master_firmware, serial_number)

    async def _get_master_firmware(self, serial_number: str):
        """
        Retrieve the master wall controller firmware version.
        """
        status = await self.get_ac_status(serial_number)
        return (
            status.get("lastKnownState", {})
            .get("AirconSystem", {})
            .get("MasterWCFirmwareVersion")
        )

    async def get_outdoor_unit_model(self, serial_number: str):
        """
        Retrieve the outdoor unit model.
        """
        return await self._handle_request(self._get_outdoor_unit_model, serial_number)

    async def _get_outdoor_unit_model(self, serial_number: str):
        """
        Retrieve the outdoor unit model.
        """
        status = await self.get_ac_status(serial_number)
        return (
            status.get("lastKnownState", {})
            .get("AirconSystem", {})
            .get("OutdoorUnit", {})
            .get("ModelNumber")
        )

    async def get_status(self, serial_number: str):
        """
        Retrieve the status of the AC system, including zones and other components.
        """
        return await self._handle_request(self._get_status, serial_number)

    async def _get_status(self, serial_number: str):
        """
        Retrieve the status of the AC system, including zones and other components.
        """
        status = await self.get_ac_status(serial_number)
        return status

    async def get_zones(self, serial_number: str):
        """Retrieve zone information."""
        return await self._handle_request(self._get_zones, serial_number)

    async def _get_zones(self, serial_number: str):
        """Retrieve zone information."""
        status = await self.get_ac_status(serial_number)
        return status.get("lastKnownState", {}).get("RemoteZoneInfo", [])

    async def get_zone_status(self, serial_number: str):
        """Retrieve zone status."""
        return await self._handle_request(self._get_zone_status, serial_number)

    async def _get_zone_status(self, serial_number: str):
        """Retrieve zone status."""
        status = await self.get_ac_status(serial_number)
        return status.get("lastKnownState", {}).get("UserAirconSettings", {}).get("EnabledZones", [])

    async def set_zone(self, serial_number: str, zone_number: int, is_enabled: bool):
        """
        Turn a specific zone ON/OFF.

        :param serial_number: Serial number of the AC system.
        :param zone_number: Zone number to control (starting from 0).
        :param is_enabled: True to turn ON, False to turn OFF.
        """
        return await self._handle_request(
            self._set_zone, serial_number, zone_number, is_enabled
        )

    async def _set_zone(self, serial_number: str, zone_number: int, is_enabled: bool):
        """
        Turn a specific zone ON/OFF.

        :param serial_number: Serial number of the AC system.
        :param zone_number: Zone number to control (starting from 0).
        :param is_enabled: True to turn ON, False to turn OFF.
        """
        # Retrieve current zone status
        current_status = await self.get_zone_status(serial_number)

        # Update the specific zone
        current_status[zone_number] = is_enabled

        # Prepare the command
        command = {
            "command": {
                "UserAirconSettings.EnabledZones": current_status,
                "type": "set-settings",
            }
        }

        response = await self.send_command(serial_number, command)
        return response

    async def set_multiple_zones(self, serial_number: str, zone_settings: dict):
        """
        Set multiple zones ON/OFF in a single command.

        :param serial_number: Serial number of the AC system.
        :param zone_settings: A dictionary where keys are zone numbers and values are True/False to enable/disable.
        """
        return await self._handle_request(
            self._set_multiple_zones, serial_number, zone_settings
        )

    async def _set_multiple_zones(self, serial_number: str, zone_settings: dict):
        """
        Set multiple zones ON/OFF in a single command.

        :param serial_number: Serial number of the AC system.
        :param zone_settings: A dictionary where keys are zone numbers and values are True/False to enable/disable.
        """
        command = {
            "command": {
                f"UserAirconSettings.EnabledZones[{zone}]": state
                for zone, state in zone_settings.items()
            },
            "type": "set-settings",
        }

        response = await self.send_command(serial_number, command)
        return response

    async def set_fan_mode(
        self, serial_number: str, fan_mode: str, continuous: bool = False
    ):
        """
        Set the fan mode of the AC system.

        Args:
            serial_number (str): The serial number of the AC system.
            fan_mode (str): The fan mode to set (e.g., "AUTO", "LOW", "MEDIUM", "HIGH").
            continuous (bool): Whether to enable continuous fan mode.
        """
        return await self._handle_request(
            self._set_fan_mode, serial_number, fan_mode, continuous
        )

    async def _set_fan_mode(
        self, serial_number: str, fan_mode: str, continuous: bool = False
    ):
        """
        Set the fan mode of the AC system.

        Args:
            serial_number (str): The serial number of the AC system.
            fan_mode (str): The fan mode to set (e.g., "AUTO", "LOW", "MEDIUM", "HIGH").
            continuous (bool): Whether to enable continuous fan mode.
        """

        mode = fan_mode
        if continuous:
            mode = f"{fan_mode}-CONT"

        command = {
            "command": {
                "UserAirconSettings.FanMode": mode,
                "type": "set-settings",
            }
        }

        response = await self.send_command(serial_number, command)
        return response

    async def set_away_mode(
        self, serial_number: str, mode: bool = False
    ):
        """
        Set the away mode of the AC system.

        Args:
            serial_number (str): The serial number of the AC system.
            mode (bool): Whether to enable away mode.
        """
        return await self._handle_request(
            self._set_away_mode, serial_number, mode
        )

    async def _set_away_mode(
        self, serial_number: str, mode: bool = False
    ):
        """
        Set the away mode of the AC system.

        Args:
            serial_number (str): The serial number of the AC system.
            mode (bool): Whether to enable away mode.
        """

        command = {
            "command": {
                "UserAirconSettings.AwayMode": mode,
                "type": "set-settings",
            }
        }

        response = await self.send_command(serial_number, command)
        return response

    async def set_quiet_mode(
        self, serial_number: str, mode: bool = False
    ):
        """
        Set the quiet mode of the AC system.

        Args:
            serial_number (str): The serial number of the AC system.
            mode (bool): Whether to enable quiet mode.
        """
        return await self._handle_request(
            self._set_quiet_mode, serial_number, mode
        )

    async def _set_quiet_mode(
        self, serial_number: str, mode: bool = False
    ):
        """
        Set the quiet mode of the AC system.

        Args:
            serial_number (str): The serial number of the AC system.
            mode (bool): Whether to enable quiet mode.
        """

        command = {
            "command": {
                "UserAirconSettings.QuietModeEnabled": mode,
                "type": "set-settings",
            }
        }

        response = await self.send_command(serial_number, command)
        return response

    async def set_turbo_mode(
        self, serial_number: str, mode: bool = False
    ):
        """
        Set the turbo mode of the AC system.

        Args:
            serial_number (str): The serial number of the AC system.
            mode (bool): Whether to enable turbo mode.
        """
        return await self._handle_request(
            self._set_turbo_mode, serial_number, mode
        )

    async def _set_turbo_mode(
        self, serial_number: str, mode: bool = False
    ):
        """
        Set the turbo mode of the AC system.

        Args:
            serial_number (str): The serial number of the AC system.
            mode (bool): Whether to enable turbo mode.
        """
        if not self.access_token:
            raise ActronNeoAuthError(
                "Authentication required before sending commands.")

        command = {
            "command": {
                "UserAirconSettings.TurboMode.Enabled": mode,
                "type": "set-settings",
            }
        }

        response = await self.send_command(serial_number, command)
        return response

    async def set_temperature(
        self, serial_number: str, mode: str, temperature: float, zone: int = None
    ):
        """
        Set the temperature for the system or a specific zone.

        :param serial_number: Serial number of the AC system.
        :param mode: The mode for which to set the temperature. Options: 'COOL', 'HEAT', 'AUTO'.
        :param temperature: The temperature to set (floating point number).
        :param zone: Zone number to set the temperature for. Default is None (common zone).
        """
        return await self._handle_request(
            self._set_temperature, serial_number, mode, temperature, zone
        )

    async def _set_temperature(
        self, serial_number: str, mode: str, temperature: float, zone: int = None
    ):
        """
        Set the temperature for the system or a specific zone.

        :param serial_number: Serial number of the AC system.
        :param mode: The mode for which to set the temperature. Options: 'COOL', 'HEAT', 'AUTO'.
        :param temperature: The temperature to set (floating point number).
        :param zone: Zone number to set the temperature for. Default is None (common zone).
        """
        if mode.upper() not in ["COOL", "HEAT", "AUTO"]:
            raise ValueError(
                "Invalid mode. Choose from 'COOL', 'HEAT', 'AUTO'.")

        # Build the command based on mode and zone
        command = {"command": {"type": "set-settings"}}

        if zone is None:  # Common zone
            if mode.upper() == "COOL":
                command["command"]["UserAirconSettings.TemperatureSetpoint_Cool_oC"] = (
                    temperature
                )
            elif mode.upper() == "HEAT":
                command["command"]["UserAirconSettings.TemperatureSetpoint_Heat_oC"] = (
                    temperature
                )
            elif mode.upper() == "AUTO":
                # Requires both heat and cool setpoints
                if (
                    isinstance(temperature, dict)
                    and "cool" in temperature
                    and "heat" in temperature
                ):
                    command["command"][
                        "UserAirconSettings.TemperatureSetpoint_Cool_oC"
                    ] = temperature["cool"]
                    command["command"][
                        "UserAirconSettings.TemperatureSetpoint_Heat_oC"
                    ] = temperature["heat"]
                else:
                    raise ValueError(
                        "For AUTO mode, provide a dict with 'cool' and 'heat' keys for temperature."
                    )
        else:  # Specific zone
            if mode.upper() == "COOL":
                command["command"][
                    f"RemoteZoneInfo[{zone}].TemperatureSetpoint_Cool_oC"
                ] = temperature
            elif mode.upper() == "HEAT":
                command["command"][
                    f"RemoteZoneInfo[{zone}].TemperatureSetpoint_Heat_oC"
                ] = temperature
            elif mode.upper() == "AUTO":
                if (
                    isinstance(temperature, dict)
                    and "cool" in temperature
                    and "heat" in temperature
                ):
                    command["command"][
                        f"RemoteZoneInfo[{zone}].TemperatureSetpoint_Cool_oC"
                    ] = temperature["cool"]
                    command["command"][
                        f"RemoteZoneInfo[{zone}].TemperatureSetpoint_Heat_oC"
                    ] = temperature["heat"]
                else:
                    raise ValueError(
                        "For AUTO mode, provide a dict with 'cool' and 'heat' keys for temperature."
                    )
        _LOGGER.debug(f"Running {command} against {serial_number}")
        return await self.send_command(serial_number, command)

    async def update_status(self):
        """Get the updated status of the AC system."""
        for system in self.systems:
            serial = system.get("serial")

            if self.latest_event_id is None:
                self.latest_event_id = {}

            if serial not in self.latest_event_id:
                self.latest_event_id[serial] = None

            if self.status is None:
                self.status = {}

            if serial not in self.status:
                self.status[serial] = {}

            if not self.latest_event_id[serial]:
                return await self._handle_request(self._fetch_full_update, serial)
            else:
                return await self._handle_request(self._fetch_incremental_updates, serial)

    async def _fetch_full_update(self, serial_number: str):
        """Fetch the full update."""
        _LOGGER.debug("Fetching full-status-broadcast")
        try:
            events = await self.get_ac_events(serial_number, event_type="latest")
            if events is None:
                _LOGGER.error("Failed to fetch events: get_ac_events returned None")
                return self.status[serial_number]
        except (TimeoutError, aiohttp.ClientError) as e:
            _LOGGER.error("Error fetching full update: %s", e)
            return self.status[serial_number]

        for event in events["events"]:
            event_data = event["data"]
            event_id = event["id"]
            event_type = event["type"]

            if event_type == "full-status-broadcast":
                _LOGGER.debug("Received full-status-broadcast, updating full state")
                self.status[serial_number] = event_data
                self.latest_event_id[serial_number] = event_id
                return self.status[serial_number]

        return self.status[serial_number]

    async def _fetch_incremental_updates(self, serial_number: str):
        """Fetch incremental updates since the last event."""
        _LOGGER.debug("Fetching incremental updates")
        try:
            events = await self.get_ac_events(
                serial_number,
                event_type="newer",
                event_id=self.latest_event_id[serial_number],
            )
            if events is None:
                _LOGGER.error("Failed to fetch events: get_ac_events returned None")
                return self.status[serial_number]
        except (TimeoutError, aiohttp.ClientError) as e:
            _LOGGER.error("Error fetching incremental updates: %s", e)
            return self.status[serial_number]

        for event in reversed(events["events"]):
            event_data = event["data"]
            event_id = event["id"]
            event_type = event["type"]

            if event_type == "full-status-broadcast":
                _LOGGER.debug("Received full-status-broadcast, updating full state")
                self.status[serial_number] = event_data
                self.latest_event_id[serial_number] = event_id
                return self.status[serial_number]

            if event_type == "status-change-broadcast":
                _LOGGER.debug("Merging status-change-broadcast into full state")
                self._merge_incremental_update(self.status[serial_number], event["data"])

            self.latest_event_id[serial_number] = event_id
        return self.status[serial_number]

    def _merge_incremental_update(self, full_state, incremental_data):
        """Merge incremental updates into the full state."""
        for key, value in incremental_data.items():
            if key.startswith("@"):
                continue

            keys = key.split(".")
            current = full_state

            for part in keys[:-1]:
                match = re.match(r"(.+)\[(\d+)\]$", part)
                if match:
                    array_key, index = match.groups()
                    index = int(index)

                    if array_key not in current:
                        current[array_key] = []

                    while len(current[array_key]) <= index:
                        current[array_key].append({})

                    current = current[array_key][index]
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

            final_key = keys[-1]
            match = re.match(r"(.+)\[(\d+)\]$", final_key)
            if match:
                array_key, index = match.groups()
                index = int(index)

                if array_key not in current:
                    current[array_key] = []

                while len(current[array_key]) <= index:
                    current[array_key].append({})

                if isinstance(current[array_key][index], dict) and isinstance(value, dict):
                    current[array_key][index].update(value)
                else:
                    current[array_key][index] = value
            else:
                current[final_key] = value
