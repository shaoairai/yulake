from flask import Blueprint, jsonify

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return jsonify({
        'message': 'Yulake API is running',
        'status': 'ok'
    })


@bp.route('/health')
def health():
    return jsonify({'status': 'healthy'})
