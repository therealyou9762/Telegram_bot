from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


@app.route('/')
def index():
    # Здесь можно отобразить основные настройки и статистику
    return render_template('index.html')


@app.route('/sources', methods=['GET', 'POST'])
def manage_sources():
    user_id = 1  # TODO: Заменить на управление пользователями на основе сессий
    if request.method == 'POST':
        new_source = request.form['source_url']
        try:
            with sqlite3.connect('news_bot.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT sources FROM users WHERE user_id = ?", (user_id,))
                sources = cursor.fetchone()
                sources_str = sources[0] if sources else ""
                sources_list = sources_str.split(';') if sources_str else []
                if new_source not in sources_list:
                    sources_list.append(new_source)
                    cursor.execute("UPDATE users SET sources = ? WHERE user_id = ?", (';'.join(sources_list), user_id))
                    conn.commit()
        except Exception as e:
            return f"Error: {e}", 500
        return redirect(url_for('manage_sources'))

    # GET: показать текущие источники
    try:
        with sqlite3.connect('news_bot.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sources FROM users WHERE user_id = ?", (user_id,))
            sources = cursor.fetchone()
            sources_str = sources[0] if sources else ""
            sources_list = sources_str.split(';') if sources_str else []
    except Exception as e:
        return f"Error: {e}", 500
    return render_template('sources.html', sources=sources_list)


# TODO: Добавить endpoints для управления ключевыми словами, черным списком и т.д.

if __name__ == '__main__':
    app.run(debug=True)