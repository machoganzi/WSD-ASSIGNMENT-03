from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.application_service import ApplicationService

application_bp = Blueprint('applications', __name__)
application_service = None

@application_bp.record
def record_params(setup_state):
    global application_service
    app = setup_state.app
    application_service = ApplicationService(app.db)

@application_bp.route('', methods=['POST'])
@jwt_required()
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
def get_user_applications():
    """지원 내역 조회 API"""
    try:
        user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        
        result = application_service.get_user_applications(user_id, page)
        
        if result['status'] == 'success':
            return jsonify(result), 200
        return jsonify(result), 400

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500