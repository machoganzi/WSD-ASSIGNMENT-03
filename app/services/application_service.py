from typing import Dict, Tuple, Optional
from datetime import datetime
from bson import ObjectId

class ApplicationService:
    def __init__(self, db):
        self.db = db
        self.ITEMS_PER_PAGE = 20

    def apply_job(self, user_id: str, job_id: str, data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """채용공고 지원"""
        try:
            # 이미 지원한 공고인지 확인
            existing_application = self.db.applications.find_one({
                'user_id': user_id,
                'job_posting_id': job_id
            })
            
            if existing_application:
                return False, "Already applied to this job", None

            # 채용공고 존재 확인
            job = self.db.job_postings.find_one({
                '_id': ObjectId(job_id),
                'status': 'active'
            })
            
            if not job:
                return False, "Job posting not found or inactive", None

            application_data = {
                'user_id': user_id,
                'job_posting_id': job_id,
                'status': 'applied',
                'resume_url': data.get('resume_url'),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = self.db.applications.insert_one(application_data)
            application_data['_id'] = str(result.inserted_id)
            
            return True, "Successfully applied to job", application_data

        except Exception as e:
            return False, str(e), None

    def cancel_application(self, user_id: str, application_id: str) -> Tuple[bool, str]:
        """지원 취소"""
        try:
            result = self.db.applications.delete_one({
                '_id': ObjectId(application_id),
                'user_id': user_id
            })
            
            if result.deleted_count:
                return True, "Application cancelled successfully"
            return False, "Application not found"

        except Exception as e:
            return False, str(e)

    def get_user_applications(self, user_id: str, page: int = 1) -> Dict:
        """사용자의 지원 내역 조회"""
        try:
            query = {'user_id': user_id}
            
            # 페이지네이션
            total_items = self.db.applications.count_documents(query)
            total_pages = (total_items + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
            
            skip = (page - 1) * self.ITEMS_PER_PAGE
            
            applications = list(self.db.applications.find(query)
                              .sort('created_at', -1)
                              .skip(skip)
                              .limit(self.ITEMS_PER_PAGE))

            # 지원한 채용공고 정보 추가
            for app in applications:
                app['_id'] = str(app['_id'])
                job = self.db.job_postings.find_one({'_id': ObjectId(app['job_posting_id'])})
                if job:
                    job['_id'] = str(job['_id'])
                    app['job_posting'] = job

            return {
                'status': 'success',
                'data': applications,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_items': total_items
                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }