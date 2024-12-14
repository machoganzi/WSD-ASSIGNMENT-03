from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from ..services.bookmark_service import BookmarkService

bookmark_bp = Blueprint('bookmarks', __name__, url_prefix='/bookmarks')
bookmark_service = None

@bookmark_bp.record
def record_params(setup_state):
    """Blueprint에 필요한 의존성을 주입합니다."""
    global bookmark_service
    app = setup_state.app
    bookmark_service = BookmarkService(app.db)

@bookmark_bp.route('', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Bookmarks'],
    'summary': '북마크 추가/제거',
    'description': '채용공고를 북마크에 추가하거나 제거합니다. 이미 북마크된 공고는 제거되고, 북마크되지 않은 공고는 추가됩니다.',
    'security': [{'bearerAuth': []}],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'required': ['job_id'],
                    'properties': {
                        'job_id': {
                            'type': 'string',
                            'description': '채용공고 ID'
                        }
                    }
                }
            }
        }
    },
    'responses': {
        '200': {
            'description': '북마크 토글 성공',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'status': {'type': 'string', 'example': 'success'},
                            'message': {'type': 'string'},
                            'data': {
                                'type': 'object',
                                'properties': {
                                    'action': {'type': 'string', 'enum': ['added', 'removed']},
                                    'bookmark': {
                                        'type': 'object',
                                        'properties': {
                                            'bookmark_id': {'type': 'string'},
                                            'job_posting_id': {'type': 'string'},
                                            'created_at': {'type': 'string', 'format': 'date-time'}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
})
def toggle_bookmark():
    """채용공고를 북마크에 추가하거나 제거하는 API입니다."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'job_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Job ID is required'
            }), 400

        success, message, result = bookmark_service.toggle_bookmark(
            user_id, data['job_id']
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': message,
                'data': result
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
    'tags': ['Bookmarks'],
    'summary': '북마크 목록 조회',
    'description': '사용자의 북마크 목록을 조회합니다. 페이지네이션, 정렬, 필터링 기능을 제공합니다.',
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'in': 'query',
            'name': 'page',
            'schema': {'type': 'integer', 'default': 1},
            'description': '조회할 페이지 번호'
        },
        {
            'in': 'query',
            'name': 'sort_by',
            'schema': {
                'type': 'string',
                'enum': ['created_at', 'company', 'category'],
                'default': 'created_at'
            },
            'description': '정렬 기준 필드'
        },
        {
            'in': 'query',
            'name': 'sort_order',
            'schema': {
                'type': 'string',
                'enum': ['asc', 'desc'],
                'default': 'desc'
            },
            'description': '정렬 순서'
        },
        {
            'in': 'query',
            'name': 'category',
            'schema': {'type': 'string'},
            'description': '채용공고 카테고리 필터'
        },
        {
            'in': 'query',
            'name': 'company_id',
            'schema': {'type': 'string'},
            'description': '회사 ID 필터'
        }
    ],
    'responses': {
        '200': {
            'description': '북마크 목록 조회 성공',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'status': {'type': 'string'},
                            'data': {
                                'type': 'array',
                                'items': {
                                    '$ref': '#/components/schemas/BookmarkedJob'
                                }
                            },
                            'pagination': {
                                'type': 'object',
                                'properties': {
                                    'currentPage': {'type': 'integer'},
                                    'totalPages': {'type': 'integer'},
                                    'totalItems': {'type': 'integer'},
                                    'perPage': {'type': 'integer'}
                                }
                            },
                            'filters': {
                                'type': 'object',
                                'properties': {
                                    'category': {'type': 'string'},
                                    'company_id': {'type': 'string'}
                                }
                            },
                            'sorting': {
                                'type': 'object',
                                'properties': {
                                    'field': {'type': 'string'},
                                    'order': {'type': 'string'}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_user_bookmarks():
    """사용자의 북마크 목록을 조회하는 API입니다."""
    try:
        user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = -1 if request.args.get('sort_order', 'desc') == 'desc' else 1
        category = request.args.get('category')
        company_id = request.args.get('company_id')
        
        result = bookmark_service.get_user_bookmarks(
            user_id=user_id,
            page=page,
            sort_by=sort_by,
            sort_order=sort_order,
            category=category,
            company_id=company_id
        )
        
        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500