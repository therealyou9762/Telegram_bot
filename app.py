import os
from flask import Flask, render_template, request, jsonify
from database import get_user, update_user, get_user_stats, init_db
from config import Config
from rq import Queue
from worker import conn
from utils import count_words_at_url



q = Queue(connection=conn)
result = q.enqueue(count_words_at_url, 'http://heroku.com')
app = Flask(__name__)
app.config.from_object(Config)

init_db()


@app.route('/')
def index():
    return render_template('index.html')


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
            return jsonify({'status': 'error', 'message': str(e)}), 400

    return jsonify({'status': 'error'}), 400


@app.route('/stats/<int:user_id>')
def stats(user_id):
    stats_data = get_user_stats(user_id, 7)
    return render_template('stats.html', stats_data=stats_data, user_id=user_id)


@app.route('/api/stats/<int:user_id>')
def api_stats(user_id):
    stats_data = get_user_stats(user_id, 7)
    return jsonify([dict(row) for row in stats_data])


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
