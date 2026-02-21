import asyncio
import asyncpg

DB_NAME = "tgbotteadb"
DB_USER = "nastya"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = 5432
SCHEMA_NAME = "bot_schema"


async def reset_database():
    conn = await asyncpg.connect(
        user=DB_USER, password=DB_PASSWORD,
        database="postgres", host=DB_HOST, port=DB_PORT
    )

    # Удаляем старую базу
    await conn.execute(f'DROP DATABASE IF EXISTS {DB_NAME}')
    print(f"База {DB_NAME} удалена")

    # Создаем новую базу
    await conn.execute(f'CREATE DATABASE {DB_NAME}')
    print(f"База {DB_NAME} создана заново")
    await conn.close()


async def create_schema_and_tables():
    conn = await asyncpg.connect(
        user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME, host=DB_HOST, port=DB_PORT
    )

    # Создаем схему, если её нет
    await conn.execute(f'CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}')

    # Проверяем, существует ли таблица user_table
    user_table_exists = await conn.fetchval(
        """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
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
                is_admin BOOLEAN DEFAULT FALSE,
                is_approve BOOLEAN DEFAULT FALSE
            )
        """)
    else:
        print("user_table уже существует, админ не добавлен")

    # Проверяем, существует ли таблица transaction_table
    transaction_table_exists = await conn.fetchval(
        """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = $1 AND table_name = 'transaction_table'
        )
        """, SCHEMA_NAME
    )

    if not transaction_table_exists:
        await conn.execute(f"""
            CREATE TABLE {SCHEMA_NAME}.transaction_table(
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES {SCHEMA_NAME}.user_table(id),
                number VARCHAR(255) NOT NULL,
                date_of_approve TIMESTAMP,
                admin_id INTEGER REFERENCES {SCHEMA_NAME}.user_table(id)
            )
        """)
        print("transaction_table создана")
    else:
        print("transaction_table уже существует")

    await conn.close()


async def main():
    await reset_database()  # Можно закомментировать, если не хотим сбрасывать базу
    await create_schema_and_tables()
    print("Схема и таблицы проверены/созданы")


async def insert_new_record_in_transaction_table(user_id: int, number: str, date_of_approve: str | None, admin_id: int | None):
    conn = await asyncpg.connect(
        user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME, host=DB_HOST, port=DB_PORT
    )

    await conn.execute(f"""
        INSERT INTO {SCHEMA_NAME}.transaction_table (user_id, number, date_of_approve, admin_id)
        VALUES ($1, $2, $3, $4)
    """, user_id, number, date_of_approve, admin_id)
    
if __name__ == "__main__":
    asyncio.run(main())