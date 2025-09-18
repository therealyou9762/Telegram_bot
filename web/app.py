import os
import logging
from flask import Flask, render_template, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import functions when they're needed to avoid circular imports
app = Flask(__name__)

def get_database_functions():
    """Lazy import database functions to avoid circular imports"""
    try:
        from db.database import get_user, update_user, get_user_stats, init_db
        return get_user, update_user, get_user_stats, init_db
    except ImportError:
        logger.error("Could not import database functions")
        return None, None, None, None

# Initialize database when app starts
try:
    _, _, _, init_db = get_database_functions()
    if init_db:
        init_db()
except Exception as e:
    logger.error(f"Ошибка инициализации базы данных: {e}")

@app.route('/api/news_stats/<int:user_id>')
def api_news_stats(user_id):
    try:
        get_user, update_user, get_user_stats, init_db = get_database_functions()
        if get_user_stats:
            stats = get_user_stats(user_id, 7)
            return jsonify([dict(row) for row in stats])
        else:
            return jsonify({'error': 'Database functions not available'}), 500
    except Exception as e:
        logger.error(e)
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    user_id = request.args.get("user_id")
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return "User invalid"
    
    get_user, update_user, get_user_stats, init_db = get_database_functions()
    if not get_user:
        return "Database not available"
        
    user = get_user(user_id)
    if not user:
        return "User invalid"
    return render_template('index.html', user=user)

@app.route('/settings/<int:user_id>')
def settings(user_id):
    get_user, update_user, get_user_stats, init_db = get_database_functions()
    if not get_user:
        return "Database not available", 500
        
    user = get_user(user_id)
    if not user:
        return "User not found", 404
    return render_template('settings.html', user=user)

@app.route('/api/update_setting/<int:user_id>', methods=['POST'])
def update_setting(user_id):
    get_user, update_user, get_user_stats, init_db = get_database_functions()
    if not update_user:
        return jsonify({'status': 'error', 'message': 'Database not available'}), 500
        
    data = request.get_json(force=True)
    field = data.get('field')
    value = data.get('value')
    if field and value is not None:
        try:
            update_user(user_id, field, value)
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.error(e)
            return jsonify({'status': 'error', 'message': str(e)}), 400
    return jsonify({'status': 'error'}), 400

@app.route('/stats/<int:user_id>')
def stats(user_id):
    try:
        get_user, update_user, get_user_stats, init_db = get_database_functions()
        if get_user_stats:
            stats_data = get_user_stats(user_id, 7)
            return render_template('stats.html', stats_data=stats_data, user_id=user_id)
        else:
            return "Database not available", 500
    except Exception as e:
        logger.error(e)
        return "Ошибка получения статистики", 500

@app.route('/api/stats/<int:user_id>')
def api_stats(user_id):
    try:
        get_user, update_user, get_user_stats, init_db = get_database_functions()
        if get_user_stats:
            stats_data = get_user_stats(user_id, 7)
            return jsonify([dict(row) for row in stats_data])
        else:
            return jsonify({'error': 'Database not available'}), 500
    except Exception as e:
        logger.error(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
