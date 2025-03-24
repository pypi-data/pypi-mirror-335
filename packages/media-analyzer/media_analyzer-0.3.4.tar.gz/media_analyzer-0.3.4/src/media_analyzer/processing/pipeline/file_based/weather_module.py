import math
from datetime import timedelta
from typing import ClassVar

from meteostat import Hourly, Point

from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.enums.analyzer_module import AnalyzerModule, FileModule
from media_analyzer.data.enums.classification.weather_condition import WeatherCondition
from media_analyzer.data.interfaces.image_data import ImageData, WeatherData
from media_analyzer.processing.pipeline.pipeline_module import PipelineModule


class WeatherModule(PipelineModule[ImageData]):
    """Extract weather data from the time and place an image was taken."""

    depends: ClassVar[set[AnalyzerModule]] = {FileModule.GPS}

    def process(self, data: ImageData, _: FullAnalyzerConfig) -> None:
        """Extract weather data from the time and place an image was taken."""
        if (
            not data.gps
            or not data.time
            or not data.time.datetime_utc
            or not data.gps.latitude
            or not data.gps.longitude
        ):
            return
        meteo_data = Hourly(
            Point(lat=data.gps.latitude, lon=data.gps.longitude),
            data.time.datetime_utc - timedelta(minutes=30),
            data.time.datetime_utc + timedelta(minutes=30),
        )
        meteo_data = meteo_data.fetch()
        if len(meteo_data) == 0:
            return  # pragma: no cover
        max_possible_rows = 2
        assert len(meteo_data) <= max_possible_rows
        weather = meteo_data.iloc[0]
        weather_condition = (
            None if math.isnan(weather.coco) else WeatherCondition(int(weather.coco))
        )
        data.weather = WeatherData(
            weather_recorded_at=weather.name.to_pydatetime(),
            weather_temperature=None if math.isnan(weather.temp) else weather.temp,
            weather_dewpoint=None if math.isnan(weather.dwpt) else weather.dwpt,
            weather_relative_humidity=None if math.isnan(weather.rhum) else weather.rhum,
            weather_precipitation=None if math.isnan(weather.prcp) else weather.prcp,
            weather_wind_gust=None if math.isnan(weather.wpgt) else weather.wpgt,
            weather_pressure=None if math.isnan(weather.pres) else weather.pres,
            weather_sun_hours=None if math.isnan(weather.tsun) else weather.tsun,
            weather_condition=weather_condition,
        )
