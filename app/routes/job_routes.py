from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from ..services.job_service import JobService

job_bp = Blueprint('jobs', __name__, url_prefix='/jobs')
job_service = None
PER_PAGE = 20  # 페이지당 항목 수 고정

@job_bp.record
def record_params(setup_state):
    global job_service
    app = setup_state.app
    job_service = JobService(app.db)

@job_bp.route('', methods=['GET'])
@swag_from({
    'tags': ['jobs'],
    'description': '채용공고 목록 조회 API',
    'parameters': [
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'default': 1,
            'description': '페이지 번호'
        },
        {
            'name': 'location',
            'in': 'query',
            'type': 'string',
            'description': '지역 필터'
        },
        {
            'name': 'experience_level',
            'in': 'query',
            'type': 'string',
            'description': '경력 필터'
        },
        {
            'name': 'skills',
            'in': 'query',
            'type': 'string',
            'description': '기술스택 필터 (콤마로 구분)'
        },
        {
            'name': 'sort_by',
            'in': 'query',
            'type': 'string',
            'description': '정렬 기준'
        }
    ],
    'responses': {
        '200': {
            'description': '채용공고 목록 조회 성공'
        }
    }
})
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
        if request.args.get('skills'):
            filters['skills'] = request.args.get('skills').split(',')
        
        sort_by = request.args.get('sort_by')
        
        result = job_service.get_job_postings(page, PER_PAGE, filters, sort_by)
        
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

@job_bp.route('/search', methods=['GET'])
@swag_from({
    'tags': ['jobs'],
    'description': '채용공고 검색 API',
    'parameters': [
        {
            'name': 'keyword',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': '검색 키워드'
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
            'description': '채용공고 검색 성공'
        }
    }
})
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

        result = job_service.search_jobs(keyword, page, PER_PAGE)
        
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

@job_bp.route('/<job_id>', methods=['GET'])
@swag_from({
    'tags': ['jobs'],
    'description': '채용공고 상세 조회 API',
    'parameters': [
        {
            'name': 'job_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': '채용공고 ID'
        }
    ],
    'responses': {
        '200': {
            'description': '채용공고 상세 조회 성공'
        }
    }
})
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