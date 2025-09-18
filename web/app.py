import os
import logging
from flask import Flask, render_template, request, jsonify
from database import get_user, update_user, get_user_stats, init_db
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

try:
    init_db()
except Exception as e:
    logger.error(f"Ошибка инициализации базы данных: {e}")

@app.route('/api/news_stats/<int:user_id>')
def api_news_stats(user_id):
    stats = get_news_stats(user_id)
    return jsonify([dict(row) for row in stats])

@app.route('/')
def index():
    user_id = request.args.get("user_id")
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return "User invalid"
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return "User invalid"
    # Дальше логика работы с пользователем...

@app.route('/settings/<int:user_id>')
def settings(user_id):
    user = get_user(user_id)
    if not user:
        return "User not found", 404
    return render_template('settings.html', user=user)

@app.route('/api/update_setting/<int:user_id>', methods=['POST'])
def update_setting(user_id):
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
        stats_data = get_user_stats(user_id, 7)
        return render_template('stats.html', stats_data=stats_data, user_id=user_id)
    except Exception as e:
        logger.error(e)
        return "Ошибка получения статистики", 500

@app.route('/api/stats/<int:user_id>')
def api_stats(user_id):
    try:
        stats_data = get_user_stats(user_id, 7)
        return jsonify([dict(row) for row in stats_data])
    except Exception as e:
        logger.error(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
