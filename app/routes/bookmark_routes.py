# bookmark_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.bookmark_service import BookmarkService

bookmark_bp = Blueprint('bookmarks', __name__)
bookmark_service = None

@bookmark_bp.record
def record_params(setup_state):
    global bookmark_service
    app = setup_state.app
    bookmark_service = BookmarkService(app.db)

@bookmark_bp.route('', methods=['POST'])
@jwt_required()
def toggle_bookmark():
    """북마크 추가/제거 API"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'job_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Job ID is required'
            }), 400

        success, message, action = bookmark_service.toggle_bookmark(
            user_id, data['job_id']
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': message,
                'data': {'action': action}
            }), 200
        
        return jsonify({
            'status': 'error',
            'message': message
        }), 400

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bookmark_bp.route('', methods=['GET'])
@jwt_required()
def get_user_bookmarks():
    """북마크 목록 조회 API"""
    try:
        user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        
        result = bookmark_service.get_user_bookmarks(user_id, page)
        
        if result['status'] == 'success':
            return jsonify(result), 200
        return jsonify(result), 400

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500