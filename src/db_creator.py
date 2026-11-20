import psycopg2


class DBCreator:
    """Класс для создания таблиц и заполнения базы данных PostgreSQL."""

    def __init__(self, db_params: dict):
        self.db_params = db_params

    def create_tables(self) -> None:
        """Создает таблицы countries и aeroplanes, пересоздавая их при наличии."""
        commands = (
            """
            DROP TABLE IF EXISTS aeroplanes;
            DROP TABLE IF EXISTS countries;
            """,
            """
            CREATE TABLE countries (
                country_id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                lamin FLOAT NOT NULL,
                lamax FLOAT NOT NULL,
                lomin FLOAT NOT NULL,
                lomax FLOAT NOT NULL
            );
            """,
            """
            CREATE TABLE aeroplanes (
                aeroplane_id SERIAL PRIMARY KEY,
                country_id INT REFERENCES countries(country_id) ON DELETE CASCADE,
                icao24 VARCHAR(20) NOT NULL,
                callsign VARCHAR(20),
                origin_country VARCHAR(100),
                velocity FLOAT,
                altitude FLOAT
            );
            """
        )
        with psycopg2.connect(**self.db_params) as conn:
            with conn.cursor() as cur:
                for command in commands:
                    cur.execute(command)
        print("Таблицы успешно созданы.")

    def insert_country(self, country_data: dict) -> int:
        """Добавляет страну в таблицу countries и возвращает её country_id."""
        query = """
            INSERT INTO countries (name, lamin, lamax, lomin, lomax)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING country_id;
        """
        with psycopg2.connect(**self.db_params) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    country_data["name"],
                    country_data["lamin"],
                    country_data["lamax"],
                    country_data["lomin"],
                    country_data["lomax"]
                ))
                return cur.fetchone()[0]

    def insert_aeroplanes(self, country_id: int, aeroplanes: list[dict]) -> None:
        """Добавляет список самолетов в таблицу aeroplanes для указанной страны."""
        if not aeroplanes:
            return
        query = """
            INSERT INTO aeroplanes (country_id, icao24, callsign, origin_country, velocity, altitude)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        values = [
            (
                country_id,
                plane["icao24"],
                plane["callsign"],
                plane["origin_country"],
                plane["velocity"],
                plane["altitude"]
            )
            for plane in aeroplanes
        ]
        with psycopg2.connect(**self.db_params) as conn:
            with conn.cursor() as cur:
                cur.executemany(query, values)
