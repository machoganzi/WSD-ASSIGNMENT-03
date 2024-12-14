from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
from bson import ObjectId

class ApplicationService:
    def __init__(self, db):
        self.db = db
        self.ITEMS_PER_PAGE = 20

    def apply_job(self, user_id: str, job_id: str, data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """채용공고 지원을 처리하는 메서드입니다."""
        try:
            # 이미 지원한 공고인지 확인합니다
            existing_application = self.db.applications.find_one({
                'user_id': user_id,
                'job_posting_id': job_id,
                'status': {'$ne': 'canceled'}  # 취소된 지원은 제외
            })
            
            if existing_application:
                return False, "이미 지원한 채용공고입니다", None

            # 채용공고가 존재하고 활성 상태인지 확인합니다
            job = self.db.job_postings.find_one({
                '_id': ObjectId(job_id),
                'status': 'active'
            })
            
            if not job:
                return False, "채용공고를 찾을 수 없거나 비활성화되었습니다", None

            # 지원 데이터를 준비합니다
            application_data = {
                'user_id': user_id,
                'job_posting_id': job_id,
                'status': 'applied',
                'resume_url': data.get('resume_url'),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'resume_versions': [{
                    'version': 1,
                    'resume_url': data.get('resume_url'),
                    'status': 'active',
                    'created_at': datetime.utcnow()
                }] if data.get('resume_url') else []
            }
            
            result = self.db.applications.insert_one(application_data)
            application_data['_id'] = str(result.inserted_id)
            
            return True, "채용공고 지원이 완료되었습니다", application_data

        except Exception as e:
            return False, str(e), None

    def cancel_application(self, user_id: str, application_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """지원 취소를 처리하는 메서드입니다."""
        try:
            # 지원 상태를 'canceled'로 업데이트합니다
            result = self.db.applications.update_one(
                {
                    '_id': ObjectId(application_id),
                    'user_id': user_id,
                    'status': {'$ne': 'canceled'}
                },
                {
                    '$set': {
                        'status': 'canceled',
                        'updated_at': datetime.utcnow(),
                        'canceled_at': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count:
                updated_application = self.db.applications.find_one(
                    {'_id': ObjectId(application_id)}
                )
                updated_application['_id'] = str(updated_application['_id'])
                return True, "지원이 취소되었습니다", updated_application
                
            return False, "지원 내역을 찾을 수 없거나 이미 취소되었습니다", None

        except Exception as e:
            return False, str(e), None

    def get_user_applications(
        self, 
        user_id: str, 
        page: int = 1,
        status: str = None,
        sort_by: str = 'created_at',
        sort_order: int = -1
    ) -> Dict:
        """사용자의 지원 내역을 조회하는 메서드입니다."""
        try:
            # 기본 쿼리 조건을 설정합니다
            query = {'user_id': user_id}
            
            # 상태별 필터링을 적용합니다
            if status:
                query['status'] = status

            # 정렬 옵션을 설정합니다
            sort_options = {
                'created_at': 'created_at',
                'updated_at': 'updated_at',
                'status': 'status'
            }
            sort_field = sort_options.get(sort_by, 'created_at')
            
            # 전체 데이터 수를 계산합니다
            total_items = self.db.applications.count_documents(query)
            total_pages = (total_items + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
            skip = (page - 1) * self.ITEMS_PER_PAGE
            
            # 지원 내역을 조회합니다
            applications = list(self.db.applications.find(query)
                              .sort(sort_field, sort_order)
                              .skip(skip)
                              .limit(self.ITEMS_PER_PAGE))

            # 채용공고 정보를 함께 반환합니다
            for app in applications:
                app['_id'] = str(app['_id'])
                job = self.db.job_postings.find_one(
                    {'_id': ObjectId(app['job_posting_id'])}
                )
                if job:
                    job['_id'] = str(job['_id'])
                    app['job_posting'] = job

            return {
                'status': 'success',
                'data': applications,
                'pagination': {
                    'currentPage': page,
                    'totalPages': total_pages,
                    'totalItems': total_items,
                    'perPage': self.ITEMS_PER_PAGE
                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def update_application_status(
        self, 
        user_id: str, 
        application_id: str, 
        status: str
    ) -> Tuple[bool, str, Optional[Dict]]:
        """지원 상태를 업데이트하는 메서드입니다."""
        try:
            valid_statuses = [
                'applied', 
                'in_review', 
                'interview_scheduled', 
                'accepted', 
                'rejected', 
                'canceled'
            ]
            
            if status not in valid_statuses:
                return False, "유효하지 않은 상태값입니다", None

            # 지원 내역을 확인합니다
            application = self.db.applications.find_one({
                '_id': ObjectId(application_id),
                'user_id': user_id
            })
            
            if not application:
                return False, "지원 내역을 찾을 수 없습니다", None

            # 상태를 업데이트합니다
            result = self.db.applications.update_one(
                {'_id': ObjectId(application_id)},
                {
                    '$set': {
                        'status': status,
                        'updated_at': datetime.utcnow(),
                        f'{status}_at': datetime.utcnow()  # 상태별 타임스탬프
                    }
                }
            )
            
            if result.modified_count:
                updated_application = self.db.applications.find_one(
                    {'_id': ObjectId(application_id)}
                )
                updated_application['_id'] = str(updated_application['_id'])
                return True, "지원 상태가 업데이트되었습니다", updated_application
                
            return False, "상태 업데이트에 실패했습니다", None

        except Exception as e:
            return False, str(e), None

    def get_application_statistics(self, user_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """사용자의 지원 통계를 조회하는 메서드입니다."""
        try:
            # 상태별 통계를 집계합니다
            status_pipeline = [
                {'$match': {'user_id': user_id}},
                {
                    '$group': {
                        '_id': '$status',
                        'count': {'$sum': 1}
                    }
                }
            ]
            status_stats = list(self.db.applications.aggregate(status_pipeline))
            
            # 최근 30일간의 지원 현황을 조회합니다
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            daily_pipeline = [
                {
                    '$match': {
                        'user_id': user_id,
                        'created_at': {'$gte': thirty_days_ago}
                    }
                },
                {
                    '$group': {
                        '_id': {
                            '$dateToString': {
                                'format': '%Y-%m-%d',
                                'date': '$created_at'
                            }
                        },
                        'count': {'$sum': 1}
                    }
                },
                {'$sort': {'_id': 1}}
            ]
            daily_stats = list(self.db.applications.aggregate(daily_pipeline))

            # 카테고리별 지원 현황을 집계합니다
            category_pipeline = [
                {'$match': {'user_id': user_id}},
                {
                    '$lookup': {
                        'from': 'job_postings',
                        'localField': 'job_posting_id',
                        'foreignField': '_id',
                        'as': 'job'
                    }
                },
                {'$unwind': '$job'},
                {
                    '$group': {
                        '_id': '$job.category',
                        'count': {'$sum': 1}
                    }
                }
            ]
            category_stats = list(self.db.applications.aggregate(category_pipeline))

            # 통계 데이터를 구성합니다
            statistics = {
                'total_applications': sum(stat['count'] for stat in status_stats),
                'status_distribution': {
                    stat['_id']: stat['count'] for stat in status_stats
                },
                'daily_applications': [
                    {
                        'date': stat['_id'],
                        'count': stat['count']
                    } for stat in daily_stats
                ],
                'category_distribution': {
                    stat['_id']: stat['count'] for stat in category_stats
                }
            }
            
            return True, "통계 조회 성공", statistics

        except Exception as e:
            return False, str(e), None

    def manage_application_resume(
        self, 
        user_id: str, 
        application_id: str, 
        resume_data: Dict
    ) -> Tuple[bool, str, Optional[Dict]]:
        """지원 이력서를 관리하는 메서드입니다."""
        try:
            # 지원 내역을 확인합니다
            application = self.db.applications.find_one({
                '_id': ObjectId(application_id),
                'user_id': user_id
            })
            
            if not application:
                return False, "지원 내역을 찾을 수 없습니다", None

            # 새로운 이력서 버전을 생성합니다
            current_versions = application.get('resume_versions', [])
            new_version = {
                'version': len(current_versions) + 1,
                'resume_url': resume_data.get('resume_url'),
                'status': 'active',
                'created_at': datetime.utcnow(),
                'notes': resume_data.get('notes')
            }

            # 기존 이력서를 보관하고 새 버전을 추가합니다
            result = self.db.applications.update_one(
                {'_id': ObjectId(application_id)},
                {
                    '$push': {'resume_versions': new_version},
                    '$set': {
                        'current_resume_url': resume_data.get('resume_url'),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count:
                updated_application = self.db.applications.find_one(
                    {'_id': ObjectId(application_id)}
                )
                updated_application['_id'] = str(updated_application['_id'])
                return True, "이력서가 업데이트되었습니다", updated_application
                
            return False, "이력서 업데이트에 실패했습니다", None

        except Exception as e:
            return False, str(e), None