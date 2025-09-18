from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def get_database_functions():
    """Lazy import database functions to avoid circular imports"""
    try:
        from db.database import get_db_connection
        return get_db_connection
    except ImportError:
        return None

@app.route('/')
def index():
    # Display main settings and stats
    return render_template('index.html')

@app.route('/auth/telegram')
def auth_telegram():
    # Реализация авторизации через Telegram
    return "Telegram auth page"

@app.route('/sources', methods=['GET', 'POST'])
def manage_sources():
    get_db_connection = get_database_functions()
    if not get_db_connection:
        return "Database not available", 500
        
    user_id = 1  # Replace with actual user/session logic as needed
    if request.method == 'POST':
        new_source = request.form['source_url']
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT sources FROM users WHERE user_id = %s", (user_id,))
                sources = cursor.fetchone()
                sources_list = sources[0] if sources and sources[0] else []
                # PostgreSQL may return sources as a list/array already
                if new_source not in sources_list:
                    sources_list.append(new_source)
                    cursor.execute("UPDATE users SET sources = %s WHERE user_id = %s", (sources_list, user_id))
                    conn.commit()
        except Exception as e:
            return f"Error: {e}", 500
        return redirect(url_for('manage_sources'))

    # GET: Show current sources
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sources FROM users WHERE user_id = %s", (user_id,))
            sources = cursor.fetchone()
            sources_list = sources[0] if sources and sources[0] else []
    except Exception as e:
        return f"Error: {e}", 500
    return render_template('sources.html', sources=sources_list)

# Create additional endpoints for keywords, blacklist, etc. as needed.

if __name__ == '__main__':
    app.run(debug=True)
