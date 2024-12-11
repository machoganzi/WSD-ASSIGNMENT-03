from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from ..services.application_service import ApplicationService

application_bp = Blueprint('applications', __name__, url_prefix='/applications')
application_service = None
PER_PAGE = 20  # 페이지당 항목 수 고정

@application_bp.record
def record_params(setup_state):
    global application_service
    app = setup_state.app
    application_service = ApplicationService(app.db)

@application_bp.route('', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['applications'],
    'description': '채용공고 지원 API',
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
        '201': {
            'description': '지원 성공',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'success'},
                    'message': {'type': 'string'},
                    'data': {'type': 'object'}
                }
            }
        }
    }
})
def apply_job():
    """채용공고 지원 API"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'job_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Job ID is required'
            }), 400

        success, message, application = application_service.apply_job(
            user_id, data['job_id'], data
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': message,
                'data': application
            }), 201
        
        return jsonify({
            'status': 'error',
            'message': message
        }), 400

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@application_bp.route('/<application_id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['applications'],
    'description': '지원 취소 API',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer {access_token}'
        },
        {
            'name': 'application_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': '지원 내역 ID'
        }
    ],
    'responses': {
        '200': {
            'description': '지원 취소 성공',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'success'},
                    'message': {'type': 'string'}
                }
            }
        }
    }
})
def cancel_application(application_id):
    """지원 취소 API"""
    try:
        user_id = get_jwt_identity()
        success, message = application_service.cancel_application(user_id, application_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': message
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

@application_bp.route('', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['applications'],
    'description': '지원 내역 조회 API',
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
            'description': '지원 내역 조회 성공',
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
def get_user_applications():
    """지원 내역 조회 API"""
    try:
        user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        
        result = application_service.get_user_applications(user_id, page, PER_PAGE)
        
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