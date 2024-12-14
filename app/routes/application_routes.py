from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from ..services.application_service import ApplicationService

application_bp = Blueprint('applications', __name__, url_prefix='/applications')
application_service = None

@application_bp.record
def record_params(setup_state):
    global application_service
    app = setup_state.app
    application_service = ApplicationService(app.db)

# [기존 라우트들은 그대로 유지...]

@application_bp.route('/<application_id>/status', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Applications'],
    'summary': '지원 상태 업데이트',
    'description': '지원의 현재 상태를 업데이트합니다. 지원 프로세스의 각 단계를 추적할 수 있습니다.',
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'in': 'path',
            'name': 'application_id',
            'required': True,
            'schema': {'type': 'string'}
        }
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'required': ['status'],
                    'properties': {
                        'status': {
                            'type': 'string',
                            'enum': [
                                'applied',
                                'in_review',
                                'interview_scheduled',
                                'accepted',
                                'rejected',
                                'canceled'
                            ],
                            'description': '변경할 지원 상태'
                        }
                    }
                }
            }
        }
    },
    'responses': {
        '200': {
            'description': '상태 업데이트 성공',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'status': {'type': 'string'},
                            'message': {'type': 'string'},
                            'data': {
                                'type': 'object',
                                'properties': {
                                    'application_id': {'type': 'string'},
                                    'status': {'type': 'string'},
                                    'updated_at': {'type': 'string'}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
})
def update_application_status(application_id):
    """지원 상태를 업데이트하는 API입니다. 지원 프로세스의 각 단계를 추적할 수 있습니다."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Status is required'
            }), 400

        success, message, updated_application = application_service.update_application_status(
            user_id, application_id, data['status']
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': message,
                'data': updated_application
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

@application_bp.route('/statistics', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Applications'],
    'summary': '지원 통계 조회',
    'description': '사용자의 전체 지원 현황에 대한 통계 정보를 제공합니다.',
    'security': [{'bearerAuth': []}],
    'responses': {
        '200': {
            'description': '통계 조회 성공',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'status': {'type': 'string'},
                            'data': {
                                'type': 'object',
                                'properties': {
                                    'total_applications': {'type': 'integer'},
                                    'status_distribution': {'type': 'object'},
                                    'daily_applications': {'type': 'array'},
                                    'category_distribution': {'type': 'object'}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_application_statistics():
    """지원 통계를 조회하는 API입니다. 전체 지원 현황과 다양한 통계 정보를 제공합니다."""
    try:
        user_id = get_jwt_identity()
        success, message, statistics = application_service.get_application_statistics(user_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': message,
                'data': statistics
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

@application_bp.route('/<application_id>/resume', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Applications'],
    'summary': '이력서 업데이트',
    'description': '지원에 첨부된 이력서를 업데이트하고 버전을 관리합니다.',
    'security': [{'bearerAuth': []}],
    'parameters': [
        {
            'in': 'path',
            'name': 'application_id',
            'required': True,
            'schema': {'type': 'string'}
        }
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'required': ['resume_url'],
                    'properties': {
                        'resume_url': {
                            'type': 'string',
                            'description': '새로운 이력서 URL'
                        },
                        'notes': {
                            'type': 'string',
                            'description': '이력서 업데이트 관련 노트'
                        }
                    }
                }
            }
        }
    },
    'responses': {
        '200': {
            'description': '이력서 업데이트 성공',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'status': {'type': 'string'},
                            'message': {'type': 'string'},
                            'data': {
                                'type': 'object',
                                'properties': {
                                    'current_resume_url': {'type': 'string'},
                                    'resume_versions': {'type': 'array'}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
})
def update_application_resume(application_id):
    """지원 이력서를 업데이트하는 API입니다. 이력서의 버전 관리를 지원합니다."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'resume_url' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Resume URL is required'
            }), 400

        success, message, updated_application = application_service.manage_application_resume(
            user_id, application_id, data
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': message,
                'data': updated_application
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