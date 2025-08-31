import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config


def get_db_connection():
    return psycopg2.connect(Config.DATABASE_URL, sslmode='require')


def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(100),
                    sources TEXT[] DEFAULT '{}',
                    keywords TEXT[] DEFAULT '{}',
                    priority_keywords TEXT[] DEFAULT '{}',
                    blacklist TEXT[] DEFAULT '{}',
                    language VARCHAR(10) DEFAULT 'ru',
                    country VARCHAR(10) DEFAULT 'ru',
                    check_interval INTEGER DEFAULT 3600,
                    last_checked TIMESTAMP DEFAULT NOW()
                )
            ''')

            # Таблица статистики
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stats (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id),
                    date DATE DEFAULT CURRENT_DATE,
                    keyword TEXT,
                    count INTEGER DEFAULT 0,
                    UNIQUE(user_id, date, keyword)
                )
            ''')

            conn.commit()


def get_user(user_id):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
    return user


def update_user(user_id, field, value):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"UPDATE users SET {field} = %s WHERE user_id = %s", (value, user_id))
            conn.commit()


def add_to_array(user_id, field, value):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"UPDATE users SET {field} = array_append({field}, %s) WHERE user_id = %s", (value, user_id))
            conn.commit()


def remove_from_array(user_id, field, value):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"UPDATE users SET {field} = array_remove({field}, %s) WHERE user_id = %s", (value, user_id))
            conn.commit()


def update_stats(user_id, keyword, count=1):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO stats (user_id, date, keyword, count)
                VALUES (%s, CURRENT_DATE, %s, %s)
                ON CONFLICT (user_id, date, keyword) 
                DO UPDATE SET count = stats.count + EXCLUDED.count
            ''', (user_id, keyword, count))
            conn.commit()


def get_user_stats(user_id, days=7):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''
                SELECT date, keyword, SUM(count) as total
                FROM stats 
                WHERE user_id = %s AND date >= CURRENT_DATE - INTERVAL %s
                GROUP BY date, keyword
                ORDER BY date DESC
            ''', (user_id, f'{days} days'))
            stats = cursor.fetchall()
    return stats