from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)
auth_service = None

@auth_bp.record
def record_params(setup_state):
    global auth_service
    app = setup_state.app
    auth_service = AuthService(app.db)

@auth_bp.route('/register', methods=['POST'])
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
                    'user_id': user['_id'],
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

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
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