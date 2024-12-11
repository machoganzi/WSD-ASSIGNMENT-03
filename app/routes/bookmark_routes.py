from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from ..services.bookmark_service import BookmarkService

bookmark_bp = Blueprint('bookmarks', __name__, url_prefix='/bookmarks')
bookmark_service = None
PER_PAGE = 20  # 페이지당 항목 수 고정

@bookmark_bp.record
def record_params(setup_state):
    global bookmark_service
    app = setup_state.app
    bookmark_service = BookmarkService(app.db)

@bookmark_bp.route('', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['bookmarks'],
    'description': '북마크 추가/제거 API',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer {access_token}'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'job_id': {'type': 'string', 'description': '채용공고 ID'}
                },
                'required': ['job_id']
            }
        }
    ],
    'responses': {
        '200': {
            'description': '북마크 토글 성공',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'success'},
                    'message': {'type': 'string'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'action': {'type': 'string', 'enum': ['added', 'removed']}
                        }
                    }
                }
            }
        }
    }
})
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
@swag_from({
    'tags': ['bookmarks'],
    'description': '북마크 목록 조회 API',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer {access_token}'
        },
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'default': 1,
            'description': '페이지 번호'
        }
    ],
    'responses': {
        '200': {
            'description': '북마크 목록 조회 성공',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'success'},
                    'data': {'type': 'array'},
                    'pagination': {
                        'type': 'object',
                        'properties': {
                            'currentPage': {'type': 'integer'},
                            'totalPages': {'type': 'integer'},
                            'totalItems': {'type': 'integer'},
                            'perPage': {'type': 'integer'}
                        }
                    }
                }
            }
        }
    }
})
def get_user_bookmarks():
    """북마크 목록 조회 API"""
    try:
        user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        
        result = bookmark_service.get_user_bookmarks(user_id, page, PER_PAGE)
        
        return jsonify({
            'status': 'success',
            'data': result['data'],
            'pagination': {
                'currentPage': page,
                'totalPages': result['total_pages'],
                'totalItems': result['total_items'],
                'perPage': PER_PAGE
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500