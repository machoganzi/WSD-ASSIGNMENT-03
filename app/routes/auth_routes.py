from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.auth_service import AuthService
from flasgger import swag_from

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_service = None

@auth_bp.record
def record_params(setup_state):
   """Blueprint에 필요한 의존성을 주입합니다."""
   global auth_service
   app = setup_state.app
   auth_service = AuthService(app.db)

@auth_bp.route('/register', methods=['POST'])
@swag_from({
   'tags': ['Authentication'],
   'summary': '회원 가입',
   'requestBody': {
       'required': True,
       'content': {
           'application/json': {
               'schema': {
                   'type': 'object',
                   'required': ['email', 'password', 'name'],
                   'properties': {
                       'email': {
                           'type': 'string',
                           'format': 'email'
                       },
                       'password': {
                           'type': 'string',
                           'minLength': 8
                       },
                       'name': {
                           'type': 'string'
                       }
                   }
               }
           }
       }
   },
   'responses': {
       '201': {
           'description': '회원가입 성공',
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
                                   'user_id': {'type': 'string'},
                                   'email': {'type': 'string'}
                               }
                           }
                       }
                   }
               }
           }
       },
       '400': {
           'description': '잘못된 요청',
           'content': {
               'application/json': {
                   'schema': {
                       'type': 'object',
                       'properties': {
                           'status': {'type': 'string', 'example': 'error'},
                           'message': {'type': 'string'}
                       }
                   }
               }
           }
       }
   }
})
def register():
   """
   신규 사용자를 등록하는 API입니다.
   이메일, 비밀번호, 이름이 필수로 요구됩니다.
   비밀번호는 Base64로 인코딩되어 저장됩니다.
   """
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
@swag_from({
   'tags': ['Authentication'],
   'summary': '로그인',
   'requestBody': {
       'required': True,
       'content': {
           'application/json': {
               'schema': {
                   'type': 'object',
                   'required': ['email', 'password'],
                   'properties': {
                       'email': {'type': 'string', 'format': 'email'},
                       'password': {'type': 'string'}
                   }
               }
           }
       }
   },
   'responses': {
       '200': {
           'description': '로그인 성공',
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
                                   'access_token': {'type': 'string'},
                                   'refresh_token': {'type': 'string'},
                                   'token_type': {'type': 'string'}
                               }
                           }
                       }
                   }
               }
           }
       },
       '401': {
           'description': '인증 실패',
           'content': {
               'application/json': {
                   'schema': {
                       'type': 'object',
                       'properties': {
                           'status': {'type': 'string', 'example': 'error'},
                           'message': {'type': 'string'}
                       }
                   }
               }
           }
       }
   }
})
def login():
   """
   사용자 로그인을 처리하는 API입니다.
   성공 시 JWT access token과 refresh token을 발급합니다.
   """
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

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
@swag_from({
   'tags': ['Authentication'],
   'summary': '프로필 조회',
   'security': [{'bearerAuth': []}],
   'responses': {
       '200': {
           'description': '프로필 조회 성공',
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
                                   'user_id': {'type': 'string'},
                                   'email': {'type': 'string'},
                                   'name': {'type': 'string'},
                                   'created_at': {'type': 'string', 'format': 'date-time'},
                                   'last_login': {'type': 'string', 'format': 'date-time'}
                               }
                           }
                       }
                   }
               }
           }
       }
   }
})
def get_profile():
   """사용자 프로필 정보를 조회하는 API입니다."""
   try:
       user_id = get_jwt_identity()
       success, message, user = auth_service.get_profile(user_id)
       
       if success:
           return jsonify({
               'status': 'success',
               'message': message,
               'data': user
           }), 200
       
       return jsonify({
           'status': 'error',
           'message': message
       }), 404

   except Exception as e:
       return jsonify({
           'status': 'error',
           'message': str(e)
       }), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
@swag_from({
   'tags': ['Authentication'],
   'summary': '프로필 수정',
   'security': [{'bearerAuth': []}],
   'requestBody': {
       'required': True,
       'content': {
           'application/json': {
               'schema': {
                   'type': 'object',
                   'properties': {
                       'name': {'type': 'string'},
                       'current_password': {'type': 'string'},
                       'new_password': {'type': 'string', 'minLength': 8}
                   },
                   'anyOf': [
                       {'required': ['name']},
                       {'required': ['current_password', 'new_password']}
                   ]
               }
           }
       }
   },
   'responses': {
       '200': {
           'description': '프로필 수정 성공',
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
                                   'user_id': {'type': 'string'},
                                   'email': {'type': 'string'},
                                   'name': {'type': 'string'},
                                   'updated_at': {'type': 'string', 'format': 'date-time'}
                               }
                           }
                       }
                   }
               }
           }
       }
   }
})
def update_profile():
   """사용자 프로필 정보를 수정하는 API입니다."""
   try:
       user_id = get_jwt_identity()
       data = request.get_json()

       if 'new_password' in data and 'current_password' not in data:
           return jsonify({
               'status': 'error',
               'message': 'Current password is required to change password'
           }), 400
       
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

@auth_bp.route('/profile', methods=['DELETE'])
@jwt_required()
@swag_from({
   'tags': ['Authentication'],
   'summary': '회원 탈퇴',
   'security': [{'bearerAuth': []}],
   'requestBody': {
       'required': True,
       'content': {
           'application/json': {
               'schema': {
                   'type': 'object',
                   'required': ['password'],
                   'properties': {
                       'password': {
                           'type': 'string',
                           'description': '계정 삭제 확인을 위한 현재 비밀번호'
                       }
                   }
               }
           }
       }
   },
   'responses': {
       '200': {
           'description': '회원 탈퇴 성공',
           'content': {
               'application/json': {
                   'schema': {
                       'type': 'object',
                       'properties': {
                           'status': {'type': 'string'},
                           'message': {'type': 'string'}
                       }
                   }
               }
           }
       }
   }
})
def deactivate_account():
   """회원 탈퇴를 처리하는 API입니다."""
   try:
       user_id = get_jwt_identity()
       data = request.get_json()

       if not data or 'password' not in data:
           return jsonify({
               'status': 'error',
               'message': 'Password is required for account deactivation'
           }), 400

       success, message, _ = auth_service.deactivate_account(user_id, data['password'])
       
       if success:
           return jsonify({
               'status': 'success',
               'message': message
           }), 200
       
       return jsonify({
           'status': 'error',
           'message': message
       }), 404

   except Exception as e:
       return jsonify({
           'status': 'error',
           'message': str(e)
       }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@swag_from({
   'tags': ['Authentication'],
   'summary': '토큰 갱신',
   'security': [{'bearerAuth': []}],
   'requestBody': {
       'required': True,
       'content': {
           'application/json': {
               'schema': {
                   'type': 'object',
                   'required': ['refresh_token'],
                   'properties': {
                       'refresh_token': {
                           'type': 'string',
                           'description': '갱신에 사용할 refresh token'
                       }
                   }
               }
           }
       }
   },
   'responses': {
       '200': {
           'description': '토큰 갱신 성공',
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
                                   'access_token': {'type': 'string'},
                                   'token_type': {'type': 'string', 'example': 'Bearer'}
                               }
                           }
                       }
                   }
               }
           }
       }
   }
})
def refresh():
   """Access Token을 갱신하는 API입니다."""
   try:
       user_id = get_jwt_identity()
       data = request.get_json()

       if not data or 'refresh_token' not in data:
           return jsonify({
               'status': 'error',
               'message': 'Refresh token is required'
           }), 400

       success, message, result = auth_service.refresh_token(user_id, data['refresh_token'])
       
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