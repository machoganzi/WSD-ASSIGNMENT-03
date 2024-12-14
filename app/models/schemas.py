from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, EmailStr

class Company(BaseModel):
    """회사 정보 모델
    
    사람인 채용공고에서 추출 가능한 회사 정보를 포함합니다.
    회사명을 기준으로 유니크하게 관리됩니다.
    """
    id: str = Field(default_factory=str)
    name: str  # 회사명 (unique)
    location: str  # 회사 위치
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WorkConditions(BaseModel):
    """근무조건 상세 정보 모델
    
    채용공고의 상세 페이지에서 추출되는 근무조건 정보를 구조화합니다.
    """
    location: str = ""  # 근무지 상세
    job_type: str = ""  # 상세 고용형태
    work_shift: str = ""  # 근무시간 상세

class JobPosting(BaseModel):
    """채용 공고 모델
    
    사람인 크롤러를 통해 수집되는 실제 데이터 필드들을 반영합니다.
    company_id, title을 기준으로 유니크하게 관리됩니다.
    """
    # 기본 식별 정보
    id: str = Field(default_factory=str)
    company_id: str
    company_name: str
    title: str
    original_url: str  # 원본 채용공고 URL
    
    # 상세 설명
    description: str = ""  # 직무 상세 설명
    
    # 직무 세부 정보
    tasks: List[str] = Field(default_factory=list)  # 담당업무
    requirements: List[str] = Field(default_factory=list)  # 자격요건
    preferred: List[str] = Field(default_factory=list)  # 우대사항
    benefits: List[str] = Field(default_factory=list)  # 복리후생
    process: List[str] = Field(default_factory=list)  # 채용 절차
    
    # 근무 조건 
    location: str = ""  # 근무지 주소
    detail_location: str = ""  # 상세 근무지
    job_type: str = ""  # 고용형태
    experience_level: str = ""  # 경력 요건
    education: str = ""  # 학력 요건
    conditions: WorkConditions = Field(default_factory=WorkConditions)  # 상세 근무조건
    
    # 급여 정보
    salary_text: str = ""  # 텍스트형 급여 정보
    
    # 직무 분야
    sector: str = ""  # 직무분야
    skills: List[str] = Field(default_factory=list)  # 기술 스택 목록
    
    # 채용 정보
    deadline: str = ""  # 마감일 텍스트
    deadline_timestamp: Optional[datetime] = None  # 파싱된 마감일
    
    # 메타 정보
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "company_name": "테크 컴퍼니",
                "title": "Python 백엔드 개발자",
                "description": "백엔드 개발팀에서 새로운 서비스 개발 및 유지보수를 담당할 개발자를 모집합니다.",
                "tasks": [
                    "백엔드 서비스 개발",
                    "API 설계 및 구현",
                    "데이터베이스 설계 및 최적화"
                ],
                "requirements": [
                    "Python 개발 경력 3년 이상",
                    "웹 프레임워크 사용 경험"
                ],
                "preferred": [
                    "Kubernetes 경험자",
                    "MSA 설계 경험"
                ],
                "benefits": [
                    "점심식사 제공",
                    "자유로운 휴가사용",
                    "원격근무 가능"
                ],
                "conditions": {
                    "location": "서울특별시 강남구 테헤란로 123",
                    "job_type": "정규직 (수습 3개월)",
                    "work_shift": "주 5일 (월-금) 09:00-18:00"
                },
                "location": "서울 강남구",
                "detail_location": "서울특별시 강남구 테헤란로 123",
                "job_type": "정규직",
                "salary_text": "3,500~4,000만원",
                "sector": "웹개발",
                "original_url": "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=12345"
            }
        }

class User(BaseModel):
    """사용자 정보 모델
    
    사용자의 기본 정보와 인증 관련 정보를 포함합니다.
    이메일을 기준으로 유니크하게 관리됩니다.
    """
    id: str = Field(default_factory=str)
    email: EmailStr
    password: str  # Base64로 인코딩된 비밀번호
    name: str
    is_active: bool = True
    last_login: Optional[datetime] = None
    refresh_token: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deactivated_at: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "홍길동",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }

class Application(BaseModel):
    """채용공고 지원 정보 모델
    
    사용자의 채용공고 지원 정보를 관리합니다.
    user_id와 job_posting_id 조합으로 유니크하게 관리됩니다.
    """
    id: str = Field(default_factory=str)
    user_id: str
    job_posting_id: str
    status: str  # applied, in_review, interview_scheduled, accepted, rejected, canceled
    resume_url: Optional[str] = None
    resume_versions: List[Dict] = Field(default_factory=list)
    current_resume_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    canceled_at: Optional[datetime] = None
    
    # 상태 변경 타임스탬프
    applied_at: Optional[datetime] = None
    in_review_at: Optional[datetime] = None
    interview_scheduled_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "status": "applied",
                "resume_url": "https://example.com/resume.pdf",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }

class Bookmark(BaseModel):
    """채용공고 북마크 모델
    
    사용자가 관심있는 채용공고를 북마크로 저장합니다.
    user_id와 job_posting_id 조합으로 유니크하게 관리됩니다.
    """
    id: str = Field(default_factory=str)
    user_id: str
    job_posting_id: str
    job_category: Optional[str] = None  # 필터링을 위한 채용공고 카테고리
    company_id: Optional[str] = None    # 필터링을 위한 회사 ID
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "job_category": "Backend Development",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }