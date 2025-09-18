-- Категории
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- Ключевые слова
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    word TEXT NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL
);

-- Новости
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    summary TEXT,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    published_at TIMESTAMP NOT NULL
);

-- Пользовательские настройки (для одного пользователя)
CREATE TABLE user_settings (
    id SERIAL PRIMARY KEY,
    telegram_user_id BIGINT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
