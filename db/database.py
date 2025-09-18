import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'], cursor_factory=RealDictCursor)

def add_news_stat(user_id, keyword, source, found_count, date):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO news_stats (user_id, keyword, source, found_count, date)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, keyword, source, found_count, date))

def get_news_stats(user_id=None, days=7):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if user_id:
                cur.execute("""
                    SELECT keyword, source, SUM(found_count) AS total, date
                    FROM news_stats
                    WHERE user_id = %s AND date > (now() - interval '%s days')
                    GROUP BY keyword, source, date
                    ORDER BY date DESC
                """, (user_id, days))
            else:
                cur.execute("""
                    SELECT keyword, source, SUM(found_count) AS total, date
                    FROM news_stats
                    WHERE date > (now() - interval '%s days')
                    GROUP BY keyword, source, date
                    ORDER BY date DESC
                """, (days,))
            return cur.fetchall()

# --- Категории ---
def add_category(name):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO categories (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id", (name,))
            result = cur.fetchone()
            return result['id'] if result else None

def get_categories():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM categories")
            return cur.fetchall()

# --- Ключевые слова ---
def add_keyword(word, category_name):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Найти или создать категорию
            cur.execute("SELECT id FROM categories WHERE name=%s", (category_name,))
            cat = cur.fetchone()
            if not cat:
                cur.execute("INSERT INTO categories (name) VALUES (%s) RETURNING id", (category_name,))
                cat = cur.fetchone()
            cat_id = cat['id']
            cur.execute("INSERT INTO keywords (word, category_id) VALUES (%s, %s) RETURNING id", (word, cat_id))
            return cur.fetchone()['id']

def get_keywords():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT k.word, c.name AS category 
                FROM keywords k LEFT JOIN categories c ON k.category_id = c.id
            """)
            return cur.fetchall()

# --- Новости ---
def add_news(title, url, summary, category_name, published_at):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Найти или создать категорию
            cur.execute("SELECT id FROM categories WHERE name=%s", (category_name,))
            cat = cur.fetchone()
            if not cat:
                cur.execute("INSERT INTO categories (name) VALUES (%s) RETURNING id", (category_name,))
                cat = cur.fetchone()
            cat_id = cat['id']
            cur.execute("""
                INSERT INTO news (title, url, summary, category_id, published_at) 
                VALUES (%s, %s, %s, %s, %s)
            """, (title, url, summary, cat_id, published_at))

def get_news(category_name=None):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if category_name:
                cur.execute("""
                    SELECT n.title, n.url, n.summary, n.published_at, c.name AS category
                    FROM news n LEFT JOIN categories c ON n.category_id = c.id
                    WHERE c.name = %s
                    ORDER BY n.published_at DESC
                """, (category_name,))
            else:
                cur.execute("""
                    SELECT n.title, n.url, n.summary, n.published_at, c.name AS category
                    FROM news n LEFT JOIN categories c ON n.category_id = c.id
                    ORDER BY n.published_at DESC
                """)
            return cur.fetchall()
