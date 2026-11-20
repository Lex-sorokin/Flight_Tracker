import time
import requests
from abc import ABC, abstractmethod


class BaseAPIClient(ABC):
    """Абстрактный базовый класс для работы с внешними API."""

    @abstractmethod
    def get_data(self, *args, **kwargs):
        """Метод получения данных от API."""
        pass


class NominatimAPI(BaseAPIClient):
    """Клиент для получения географических границ стран через Nominatim API."""

    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"   # исправления по документации
        self.headers = {"User-Agent": "FlightTrackerCoursework/1.0"}  # это лицензионная подпись

    def get_data(self, country_name: str) -> dict | None:
        """
        Получает координаты bounding box для указанной страны.
        Возвращает словарь с координатами или None.
        """
        params = {
            "country": country_name,
            "format": "json",
            "limit": 1
        }
        try:
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            time.sleep(1.1)  # Соблюдение правил Nominatim (не более 1 запроса в сек)

            if data:
                bbox = data[0].get("boundingbox")  # [min_lat, max_lat, min_lon, max_lon]
                return {
                    "name": country_name,
                    "lamin": float(bbox[0]),
                    "lamax": float(bbox[1]),
                    "lomin": float(bbox[2]),
                    "lomax": float(bbox[3]),
                }
        except requests.RequestException as e:
            print(f"Ошибка при запросе координат для {country_name}: {e}")
        return None


class OpenSkyAPI(BaseAPIClient):
    """Клиент для получения данных о воздушных судах через OpenSky Network API."""

    def __init__(self):
        self.base_url = "https://opensky-network.org/api/states/all"   # по документации

    def get_data(self, bbox: dict) -> list[dict]:
        """
        Получает список самолетов в заданном квадрате координат (bounding box).
        Фильтрует самолеты, находящиеся на земле (on_ground = True).
        """
        params = {
            "lamin": bbox["lamin"],
            "lomin": bbox["lomin"],
            "lamax": bbox["lamax"],
            "lomax": bbox["lomax"],
        }
        aeroplanes = []
        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            states = data.get("states") or []

            for state in states:
                # state[8] - флаг on_ground (берем только те, что в воздухе)
                if not state[8]:
                    callsign = state[1].strip() if state[1] else "N/A"
                    aeroplanes.append({
                        "icao24": state[0],
                        "callsign": callsign,
                        "origin_country": state[2],
                        "velocity": state[9] if state[9] is not None else 0.0,
                        "altitude": state[7] if state[7] is not None else 0.0,
                    })
        except requests.RequestException as e:
            print(f"Ошибка при запросе самолетов для {bbox['name']}: {e}")

        return aeroplanes
