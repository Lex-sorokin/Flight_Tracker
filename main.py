import os
from dotenv import load_dotenv
from src.api_clients import NominatimAPI, OpenSkyAPI
from src.db_creator import DBCreator
from src.db_manager import DBManager

load_dotenv()


def get_db_params() -> dict:
    """Возвращает параметры подключения к БД из переменных окружения."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "flight_tracker"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "postgres"),
    }


def main():
    """Основная функция запуска сбора данных и демонстрации работы DBManager."""
    # 10 стран для соблюдения критерия оценки
    countries_list = [
        "Switzerland", "Germany", "France", "Spain", "Italy",
        "Poland", "Austria", "Netherlands", "Belgium", "Czechia"
    ]

    db_params = get_db_params()
    nominatim = NominatimAPI()
    opensky = OpenSkyAPI()
    db_creator = DBCreator(db_params)

    print("1. Создание таблиц в БД...")
    db_creator.create_tables()

    print("2. Сбор данных по странам и самолетам...")
    for country in countries_list:
        bbox = nominatim.get_data(country)
        if bbox:
            country_id = db_creator.insert_country(bbox)
            aeroplanes = opensky.get_data(bbox)
            db_creator.insert_aeroplanes(country_id, aeroplanes)
            print(f"   {country}: добавлено самолетов - {len(aeroplanes)}")

    # Работа с DBManager
    db_manager = DBManager(db_params)

    print("\n--- 1. Количество самолетов по странам ---")
    for row in db_manager.get_countries_and_aeroplanes_count():
        print(f"Страна: {row[0]} | Самолетов в небе: {row[1]}")

    print(f"\n--- 2. Средняя скорость самолетов ---\n{db_manager.get_avg_speed()} м/с")

    print("\n--- 3. Самолеты со скоростью выше средней (первые 5) ---")
    for row in db_manager.get_aeroplanes_with_higher_speed()[:5]:
        print(row)

    keyword = input("\nВведите ключевое слово для поиска по позывному (например, DLH или AFR): ").strip()
    print(f"\n--- 4. Результаты поиска по '{keyword}' ---")
    found = db_manager.get_aeroplanes_with_keyword(keyword)
    for row in found:
        print(row)


if __name__ == "__main__":
    main()
