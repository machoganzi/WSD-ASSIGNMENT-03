from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from ..services.job_service import JobService

job_bp = Blueprint('jobs', __name__, url_prefix='/jobs')
job_service = None
PER_PAGE = 20

@job_bp.record
def record_params(setup_state):
    global job_service
    app = setup_state.app
    job_service = JobService(app.db)

@job_bp.route('', methods=['GET'])
@swag_from({
    'tags': ['Jobs'],
    'summary': '채용공고 목록 조회',
    'parameters': [
        {
            'in': 'query',
            'name': 'page',
            'schema': {
                'type': 'integer',
                'default': 1
            }
        },
        {
            'in': 'query',
            'name': 'location',
            'schema': {
                'type': 'string'
            }
        },
        {
            'in': 'query',
            'name': 'experience_level',
            'schema': {
                'type': 'string'
            }
        },
        {
            'in': 'query',
            'name': 'min_salary',
            'schema': {
                'type': 'integer'
            }
        },
        {
            'in': 'query',
            'name': 'skills',
            'schema': {
                'type': 'string'
            },
            'description': 'Comma separated skills'
        },
        {
            'in': 'query',
            'name': 'sort_by',
            'schema': {
                'type': 'string',
                'enum': ['salary', 'deadline']
            }
        }
    ],
    'responses': {
        '200': {
            'description': '채용공고 목록',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'status': {
                                'type': 'string',
                                'example': 'success'
                            },
                            'data': {
                                'type': 'array',
                                'items': {
                                    '$ref': '#/components/schemas/JobPosting'
                                }
                            },
                            'pagination': {
                                '$ref': '#/components/schemas/Pagination'
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_job_postings():
    """채용공고 목록 조회 API"""
    try:
        # 쿼리 파라미터 가져오기
        page = request.args.get('page', 1, type=int)
        location = request.args.get('location')
        experience_level = request.args.get('experience_level')
        min_salary = request.args.get('min_salary', type=int)
        skills = request.args.get('skills')
        sort_by = request.args.get('sort_by')

        # 필터 구성
        filters = {}
        if location:
            filters['location'] = location
        if experience_level:
            filters['experience_level'] = experience_level
        if min_salary:
            filters['min_salary'] = min_salary
        if skills:
            filters['skills'] = skills.split(',')

        # 서비스 호출
        result = job_service.get_job_postings(page=page, filters=filters, sort_by=sort_by)
        
        if result['status'] == 'success':
            return jsonify(result), 200
        
        return jsonify(result), 400

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@job_bp.route('/search', methods=['GET'])
@swag_from({
    'tags': ['Jobs'],
    'summary': '채용공고 검색',
    'parameters': [
        {
            'in': 'query',
            'name': 'keyword',
            'required': True,
            'schema': {
                'type': 'string'
            }
        },
        {
            'in': 'query',
            'name': 'page',
            'schema': {
                'type': 'integer',
                'default': 1
            }
        }
    ],
    'responses': {
        '200': {
            'description': '검색 결과',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'status': {
                                'type': 'string',
                                'example': 'success'
                            },
                            'data': {
                                'type': 'array',
                                'items': {
                                    '$ref': '#/components/schemas/JobPosting'
                                }
                            },
                            'pagination': {
                                '$ref': '#/components/schemas/Pagination'
                            }
                        }
                    }
                }
            }
        }
    }
})
def search_jobs():
    """채용공고 검색 API"""
    try:
        keyword = request.args.get('keyword')
        if not keyword:
            return jsonify({
                'status': 'error',
                'message': '검색어를 입력해주세요.'
            }), 400

        page = request.args.get('page', 1, type=int)
        result = job_service.search_jobs(keyword=keyword, page=page)
        
        if result['status'] == 'success':
            return jsonify(result), 200
            
        return jsonify(result), 400

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@job_bp.route('/<job_id>', methods=['GET'])
@swag_from({
    'tags': ['Jobs'],
    'summary': '채용공고 상세 조회',
    'parameters': [
        {
            'in': 'path',
            'name': 'job_id',
            'required': True,
            'schema': {
                'type': 'string'
            }
        }
    ],
    'responses': {
        '200': {
            'description': '채용공고 상세 정보',
            'content': {
                'application/json': {
                    'schema': {
                        '$ref': '#/components/schemas/JobPosting'
                    }
                }
            }
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