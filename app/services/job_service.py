from typing import Dict, List, Tuple, Optional
from datetime import datetime
from bson import ObjectId
import math

class JobService:
    def __init__(self, db):
        """JobService 초기화: 채용공고 관련 비즈니스 로직을 처리합니다."""
        self.db = db
        self.ITEMS_PER_PAGE = 20  # 페이지당 항목 수

    def create_job_posting(self, job_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """
        채용공고 생성: 새로운 채용공고를 데이터베이스에 저장합니다.
        크롤러에서 수집한 모든 필드를 처리하고 정규화합니다.
        """
        try:
            # 기본 메타데이터 설정
            job_data['created_at'] = datetime.utcnow()
            job_data['updated_at'] = datetime.utcnow()
            job_data['status'] = 'active'
            
            # 리스트 타입 필드 정규화
            list_fields = ['tasks', 'requirements', 'preferred', 'benefits', 'skills']
            for field in list_fields:
                if field not in job_data:
                    job_data[field] = []
                elif not isinstance(job_data[field], list):
                    job_data[field] = [job_data[field]]
            
            # 문자열 필드 정규화
            string_fields = ['description', 'location', 'job_type', 'experience_level', 
                           'education', 'work_shift', 'sector', 'salary_text']
            for field in string_fields:
                if field not in job_data:
                    job_data[field] = ""
            
            # 급여 정보 정규화
            if 'salary' not in job_data or not isinstance(job_data['salary'], dict):
                job_data['salary'] = {'min': 0, 'max': 0}
            else:
                job_data['salary']['min'] = job_data['salary'].get('min', 0)
                job_data['salary']['max'] = job_data['salary'].get('max', 0)
            
            # 근무조건 정보 정규화
            if 'conditions' not in job_data or not isinstance(job_data['conditions'], dict):
                job_data['conditions'] = {
                    'location': '',
                    'job_type': '',
                    'work_shift': ''
                }
            
            # 날짜 정보 처리
            if 'deadline' in job_data and isinstance(job_data['deadline'], str):
                try:
                    deadline_text = job_data['deadline'].split('~')[1].strip() \
                        if '~' in job_data['deadline'] else job_data['deadline']
                    job_data['deadline_timestamp'] = datetime.strptime(
                        deadline_text, '%Y.%m.%d'
                    )
                except:
                    job_data['deadline_timestamp'] = None
            
            result = self.db.job_postings.insert_one(job_data)
            job_data['_id'] = str(result.inserted_id)
            
            return True, "채용공고가 성공적으로 등록되었습니다", job_data
        except Exception as e:
            return False, f"채용공고 등록 실패: {str(e)}", None

    def get_job_postings(self, page: int = 1, filters: Dict = None, sort_by: str = None) -> Dict:
        """채용공고 목록 조회: 필터링과 정렬 조건을 적용하여 채용공고 목록을 반환합니다."""
        try:
            # 기본 필터 (활성 상태)
            query = {'status': 'active'}
            
            # 고급 필터링 조건 적용
            if filters:
                if 'location' in filters:
                    query['location'] = {'$regex': filters['location'], '$options': 'i'}
                if 'experience_level' in filters:
                    query['experience_level'] = filters['experience_level']
                if 'education' in filters:
                    query['education'] = filters['education']
                if 'job_type' in filters:
                    query['job_type'] = filters['job_type']
                if 'salary' in filters:
                    query['$or'] = [
                        {'salary.min': {'$gte': filters['salary']}},
                        {'salary.max': {'$gte': filters['salary']}}
                    ]
                if 'skills' in filters:
                    query['skills'] = {'$all': filters['skills']}
                if 'sector' in filters:
                    query['sector'] = {'$regex': filters['sector'], '$options': 'i'}
                if 'deadline' in filters:
                    query['deadline_timestamp'] = {'$gte': datetime.utcnow()}
                if 'tasks' in filters:
                    query['tasks'] = {'$all': filters['tasks']}

            # 정렬 조건
            sort_conditions = [('created_at', -1)]  # 기본: 최신순
            if sort_by:
                if sort_by == 'salary':
                    sort_conditions = [('salary.max', -1)]
                elif sort_by == 'deadline':
                    sort_conditions = [('deadline_timestamp', 1)]
                elif sort_by == 'experience':
                    sort_conditions = [('experience_level', 1)]

            # 페이지네이션 처리
            total_items = self.db.job_postings.count_documents(query)
            total_pages = math.ceil(total_items / self.ITEMS_PER_PAGE)
            skip = (page - 1) * self.ITEMS_PER_PAGE
            
            # 채용공고 조회 및 회사 정보 결합
            pipeline = [
                {'$match': query},
                {'$sort': {field: order for field, order in sort_conditions}},
                {'$skip': skip},
                {'$limit': self.ITEMS_PER_PAGE},
                {
                    '$lookup': {
                        'from': 'companies',
                        'localField': 'company_id',
                        'foreignField': '_id',
                        'as': 'company'
                    }
                },
                {'$unwind': '$company'}
            ]
            
            job_postings = list(self.db.job_postings.aggregate(pipeline))

            # ObjectId 변환 및 데이터 정제
            for job in job_postings:
                job['_id'] = str(job['_id'])
                job['company_id'] = str(job['company_id'])
                job['company']['_id'] = str(job['company']['_id'])

            return {
                'status': 'success',
                'data': job_postings,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_items': total_items,
                    'items_per_page': self.ITEMS_PER_PAGE
                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f"채용공고 목록 조회 실패: {str(e)}"
            }

    def search_jobs(self, keyword: str, page: int = 1) -> Dict:
        """채용공고 검색: 키워드를 사용하여 관련 채용공고를 검색합니다."""
        try:
            # 향상된 검색 쿼리
            query = {
                '$and': [
                    {'status': 'active'},
                    {'$or': [
                        {'title': {'$regex': keyword, '$options': 'i'}},
                        {'description': {'$regex': keyword, '$options': 'i'}},
                        {'tasks': {'$regex': keyword, '$options': 'i'}},  # 담당업무 검색 추가
                        {'requirements': {'$regex': keyword, '$options': 'i'}},  # 자격요건 검색 추가
                        {'preferred': {'$regex': keyword, '$options': 'i'}},  # 우대사항 검색 추가
                        {'benefits': {'$regex': keyword, '$options': 'i'}},  # 복리후생 검색 추가
                        {'skills': {'$regex': keyword, '$options': 'i'}},
                        {'sector': {'$regex': keyword, '$options': 'i'}},
                        {'company_name': {'$regex': keyword, '$options': 'i'}},
                        {'location': {'$regex': keyword, '$options': 'i'}},
                        {'work_shift': {'$regex': keyword, '$options': 'i'}},  # 근무시간 검색 추가
                        {'conditions.location': {'$regex': keyword, '$options': 'i'}},  # 상세 근무지 검색
                        {'conditions.work_shift': {'$regex': keyword, '$options': 'i'}}  # 상세 근무시간 검색
                    ]}
                ]
            }

            # 페이지네이션
            total_items = self.db.job_postings.count_documents(query)
            total_pages = math.ceil(total_items / self.ITEMS_PER_PAGE)
            skip = (page - 1) * self.ITEMS_PER_PAGE
            
            # 회사 정보를 포함한 검색 결과 조회
            pipeline = [
                {'$match': query},
                {'$sort': {'created_at': -1}},
                {'$skip': skip},
                {'$limit': self.ITEMS_PER_PAGE},
                {
                    '$lookup': {
                        'from': 'companies',
                        'localField': 'company_id',
                        'foreignField': '_id',
                        'as': 'company'
                    }
                },
                {'$unwind': '$company'}
            ]
            
            job_postings = list(self.db.job_postings.aggregate(pipeline))

            # ObjectId 변환
            for job in job_postings:
                job['_id'] = str(job['_id'])
                job['company_id'] = str(job['company_id'])
                job['company']['_id'] = str(job['company']['_id'])

            return {
                'status': 'success',
                'data': job_postings,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_items': total_items,
                    'items_per_page': self.ITEMS_PER_PAGE
                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f"채용공고 검색 실패: {str(e)}"
            }

    def get_job_detail(self, job_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """채용공고 상세 조회: 특정 채용공고의 상세 정보를 회사 정보와 함께 반환합니다."""
        try:
            # 채용공고와 회사 정보를 한 번에 조회
            pipeline = [
                {'$match': {'_id': ObjectId(job_id)}},
                {
                    '$lookup': {
                        'from': 'companies',
                        'localField': 'company_id',
                        'foreignField': '_id',
                        'as': 'company'
                    }
                },
                {'$unwind': '$company'}
            ]
            
            job = next(self.db.job_postings.aggregate(pipeline), None)
            
            if not job:
                return False, "해당 채용공고를 찾을 수 없습니다", None

            # ObjectId 변환
            job['_id'] = str(job['_id'])
            job['company_id'] = str(job['company_id'])
            job['company']['_id'] = str(job['company']['_id'])

            return True, "채용공고 조회 성공", job

        except Exception as e:
            return False, f"채용공고 조회 실패: {str(e)}", None