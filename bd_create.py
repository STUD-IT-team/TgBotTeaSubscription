import asyncio
import asyncpg

DB_NAME = "tgbotteadb"
DB_USER = "danil"
DB_PASSWORD = "password123"
DB_HOST = "localhost"
DB_PORT = 5432
SCHEMA_NAME = "bot_schema"


async def setup_database():
    # Подключаемся к служебной базе postgres для создания базы
    conn = await asyncpg.connect(
        user=DB_USER, password=DB_PASSWORD, database="postgres",
        host=DB_HOST, port=DB_PORT
    )

    # Проверяем, существует ли база
    db_exists = await conn.fetchval(
        "SELECT 1 FROM pg_database WHERE datname = $1", DB_NAME
    )
    if not db_exists:
        await conn.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"База {DB_NAME} создана")
    else:
        print(f"База {DB_NAME} уже существует")
    await conn.close()

    # Подключаемся к новой/существующей базе
    conn = await asyncpg.connect(
        user=DB_USER, password=DB_PASSWORD, database=DB_NAME,
        host=DB_HOST, port=DB_PORT
    )

    # Создаём схему, если её нет
    await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}")
    print(f"Схема {SCHEMA_NAME} проверена/создана")

    # Создаём таблицу пользователей, если её нет
    user_table_exists = await conn.fetchval(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = $1 AND table_name = 'user_table'
        )
        """, SCHEMA_NAME
    )
    if not user_table_exists:
        await conn.execute(f"""
            CREATE TABLE {SCHEMA_NAME}.user_table(
                id SERIAL PRIMARY KEY,
                tg_id BIGINT UNIQUE,
                last_notification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                price INTEGER DEFAULT 300
            )
        """)
        print("user_table создана")
    else:
        print("user_table уже существует")

    # Создаём таблицу транзакций, если её нет
    transaction_table_exists = await conn.fetchval(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = $1 AND table_name = 'transaction_table'
        )
        """, SCHEMA_NAME
    )
    if not transaction_table_exists:
        await conn.execute(f"""
            CREATE TABLE {SCHEMA_NAME}.transaction_table(
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES {SCHEMA_NAME}.user_table(tg_id),
                number VARCHAR(255) NOT NULL,
                date_of_approve TIMESTAMP,
                admin_id INTEGER,
                price INTEGER
            )
        """)
        print("transaction_table создана")
    else:
        print("transaction_table уже существует")

    await conn.close()
    print("База, схема и таблицы готовы")


if __name__ == "__main__":
    asyncio.run(setup_database())