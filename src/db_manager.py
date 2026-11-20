import psycopg2


class DBManager:
    """Класс для взаимодействия с данными о странах и самолетах в БД PostgreSQL."""

    def __init__(self, db_params: dict):
        self.db_params = db_params

    def _execute_query(self, query: str, params: tuple = None) -> list[tuple]:
        """Вспомогательный метод для выполнения SELECT-запросов."""
        with psycopg2.connect(**self.db_params) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()

    def get_countries_and_aeroplanes_count(self) -> list[tuple]:
        """
        Получает список всех стран и количество самолетов в их воздушных пространствах.
        Использует LEFT JOIN, чтобы показать страны даже с 0 самолетов.
        """
        query = """
            SELECT c.name, COUNT(a.aeroplane_id) AS aeroplanes_count
            FROM countries c
            LEFT JOIN aeroplanes a ON c.country_id = a.country_id
            GROUP BY c.name
            ORDER BY aeroplanes_count DESC;
        """
        return self._execute_query(query)

    def get_all_aeroplanes(self) -> list[tuple]:
        """
        Получает список всех воздушных судов с указанием страны наблюдения,
        позывного, страны регистрации, скорости и высоты.
        """
        query = """
            SELECT c.name AS airspace_country, a.callsign, a.origin_country, a.velocity, a.altitude
            FROM aeroplanes a
            JOIN countries c ON a.country_id = c.country_id;
        """
        return self._execute_query(query)

    def get_avg_speed(self) -> float:
        """Получает среднюю скорость по всем самолетам в БД."""
        query = "SELECT ROUND(AVG(velocity)::numeric, 2) FROM aeroplanes WHERE velocity > 0;"
        result = self._execute_query(query)
        return float(result[0][0]) if result and result[0][0] else 0.0

    def get_aeroplanes_with_higher_speed(self) -> list[tuple]:
        """Получает список всех самолетов, у которых скорость выше средней."""
        query = """
            SELECT c.name, a.callsign, a.origin_country, a.velocity
            FROM aeroplanes a
            JOIN countries c ON a.country_id = c.country_id
            WHERE a.velocity > (SELECT AVG(velocity) FROM aeroplanes WHERE velocity > 0)
            ORDER BY a.velocity DESC;
        """
        return self._execute_query(query)

    def get_aeroplanes_with_keyword(self, keyword: str) -> list[tuple]:
        """
        Получает список всех самолетов, в позывном которых содержатся
        переданные в метод символы (без учета регистра).
        """
        query = """
            SELECT c.name, a.callsign, a.origin_country, a.velocity
            FROM aeroplanes a
            JOIN countries c ON a.country_id = c.country_id
            WHERE a.callsign ILIKE %s;
        """
        return self._execute_query(query, (f"%{keyword}%",))
