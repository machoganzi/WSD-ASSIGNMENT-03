from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.job_service import JobService

job_bp = Blueprint('jobs', __name__)
job_service = None

@job_bp.record
def record_params(setup_state):
    global job_service
    app = setup_state.app
    job_service = JobService(app.db)

@job_bp.route('', methods=['GET'])
def get_job_postings():
    """채용공고 목록 조회 API"""
    try:
        page = int(request.args.get('page', 1))
        filters = {}
        
        # 필터 파라미터 처리
        if request.args.get('location'):
            filters['location'] = request.args.get('location')
        if request.args.get('experience_level'):
            filters['experience_level'] = request.args.get('experience_level')
        if request.args.get('min_salary'):
            filters.setdefault('salary', {})['min'] = int(request.args.get('min_salary'))
        if request.args.get('skills'):
            filters['skills'] = request.args.get('skills').split(',')

        sort_by = request.args.get('sort_by')
        
        result = job_service.get_job_postings(page, filters, sort_by)
        
        if result['status'] == 'success':
            return jsonify(result), 200
        return jsonify(result), 400

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@job_bp.route('/search', methods=['GET'])
def search_jobs():
    """채용공고 검색 API"""
    try:
        keyword = request.args.get('keyword', '')
        page = int(request.args.get('page', 1))
        
        if not keyword:
            return jsonify({
                'status': 'error',
                'message': 'Search keyword is required'
            }), 400

        result = job_service.search_jobs(keyword, page)
        
        if result['status'] == 'success':
            return jsonify(result), 200
        return jsonify(result), 400

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@job_bp.route('/<job_id>', methods=['GET'])
def get_job_detail(job_id):
    """채용공고 상세 조회 API"""
    try:
        success, message, job = job_service.get_job_detail(job_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'data': job
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