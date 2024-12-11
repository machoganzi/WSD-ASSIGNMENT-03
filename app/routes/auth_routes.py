from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.auth_service import AuthService
from flasgger import swag_from

# /auth prefix 적용
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_service = None

@auth_bp.record
def record_params(setup_state):
    global auth_service
    app = setup_state.app
    auth_service = AuthService(app.db)

@auth_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['auth'],
    'description': '회원 가입 API',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'description': '이메일'},
                    'password': {'type': 'string', 'description': '비밀번호'},
                    'name': {'type': 'string', 'description': '이름'}
                },
                'required': ['email', 'password', 'name']
            }
        }
    ],
    'responses': {
        '201': {
            'description': '회원가입 성공',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'success'},
                    'message': {'type': 'string'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'user_id': {'type': 'string'},
                            'email': {'type': 'string'}
                        }
                    }
                }
            }
        }
    }
})
def register():
    """사용자 등록 API"""
    try:
        data = request.get_json()
        required_fields = ['email', 'password', 'name']
        
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields'
            }), 400

        success, message, user = auth_service.register(data)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': message,
                'data': {
                    'user_id': str(user['_id']),  # ObjectId를 문자열로 변환
                    'email': user['email']
                }
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

@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['auth'],
    'description': '로그인 API',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'description': '이메일'},
                    'password': {'type': 'string', 'description': '비밀번호'}
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        '200': {
            'description': '로그인 성공',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'success'},
                    'message': {'type': 'string'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'access_token': {'type': 'string'},
                            'refresh_token': {'type': 'string'}
                        }
                    }
                }
            }
        }
    }
})
def login():
    """로그인 API"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Email and password are required'
            }), 400

        success, message, result = auth_service.login(data['email'], data['password'])
        
        if success:
            return jsonify({
                'status': 'success',
                'message': message,
                'data': result
            }), 200
        
        return jsonify({
            'status': 'error',
            'message': message
        }), 401

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@swag_from({
    'tags': ['auth'],
    'description': '토큰 갱신 API',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Refresh Token (Bearer)'
        }
    ],
    'responses': {
        '200': {
            'description': '토큰 갱신 성공',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'success'},
                    'message': {'type': 'string'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'access_token': {'type': 'string'}
                        }
                    }
                }
            }
        }
    }
})
def refresh():
    """토큰 갱신 API"""
    try:
        user_id = get_jwt_identity()
        new_token = auth_service.refresh_token(user_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Token refreshed successfully',
            'data': {
                'access_token': new_token
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['auth'],
    'description': '프로필 수정 API',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Access Token (Bearer)'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': '이름'},
                    'password': {'type': 'string', 'description': '새 비밀번호'}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': '프로필 수정 성공'
        }
    }
})
def update_profile():
    """프로필 업데이트 API"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        success, message, updated_user = auth_service.update_profile(user_id, data)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': message,
                'data': updated_user
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