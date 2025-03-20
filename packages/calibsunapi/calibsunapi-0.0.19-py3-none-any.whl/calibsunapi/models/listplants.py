from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from calibsunapi.client import CalibsunApiClient


@dataclass
class Plant:
    site_id: str
    name: str
    latitude: str
    longitude: str
    elevation: str
    peakpower: str
    tilt: str
    azimut: str
    tilt_gti: str
    azimut_gti: str
    rendement_stc: str
    coefficient_temperature: str
    DC_AC: str
    tracker: str
    backtracking: str
    maxangle: str
    entraxe: str
    L_panel: str
    gti: str
    ghi: str
    resolution: str
    frequency: str
    production: str
    horizon: str
    subscription_type: str
    activated: str

    client: Optional["CalibsunApiClient"] = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Plant({self.name.capitalize()})"

    def push_measurements(self, format: str, data: dict[str, str] = None, filepath: str = None):
        """
        Push measurements to the server.

        Args:
            format (str): The format of the measurements data.
            data (dict[str, str], optional): A dictionary containing the measurements data. Defaults to None.
            filepath (str, optional): The file path to the measurements data file. Defaults to None.

        Returns:
            Response: The response from the server after pushing the measurements.
        """

        return self.client.push_measurements(self.site_id, format, data=data, filepath=filepath)

    def get_latest_forecast(self, target: str):
        """
        Retrieve the latest forecast for a specified target.

        Args:
            target (str): The target for which to retrieve the latest forecast.
        Returns:
            dict: The latest forecast data for the specified target.
        """

        return self.client.get_latest_forecast(self.site_id, target)

    def get_latest_forecast_probabilistic(self, target: str):
        """
        Retrieve the latest probabilistic forecast for a given target.

        Args:
            target (str): The target for which to retrieve the forecast.
        Returns:
            dict: The latest probabilistic forecast data for the specified target.
        """

        return self.client.get_latest_forecast_probabilistic(self.site_id, target)

    def get_latest_forecast_deterministic(self, target: str):
        """
        Retrieve the latest deterministic forecast for a given target.

        Args:
            target (str): The target for which the latest deterministic forecast is requested.
        Returns:
            dict: The latest deterministic forecast data for the specified target.
        """

        return self.client.get_latest_forecast_deterministic(self.site_id, target)

    def get_forecast(self, time: str, target: str):
        """
        Retrieve the forecast for a specific time and target.

        Args:
            time (str): The time for which the forecast is requested.
            target (str): The target for which the forecast is requested.
        Returns:
            dict: The forecast data retrieved from the client.
        """

        return self.client.get_forecast(self.site_id, target, time)

    def get_probabilistic_forecast(self, time: str, target: str):
        """
        Retrieve the probabilistic forecast for a given time and target.

        Args:
            time (str): The specific time for which the forecast is requested.
            target (str): The target parameter for the forecast (e.g., ghi, gti, prod).
        Returns:
            dict: A dictionary containing the probabilistic forecast data.
        """

        return self.client.get_probabilistic_forecast(self.site_id, target, time)

    def get_deterministic_forecast(self, time: str, target: str):
        """
        Retrieve the deterministic forecast for a specific time and target.

        Args:
            time (str): The time for which the forecast is requested.
            target (str): The target parameter for the forecast.
        Returns:
            dict: The deterministic forecast data retrieved from the client.
        """

        return self.client.get_deterministic_forecast(self.site_id, target, time)
