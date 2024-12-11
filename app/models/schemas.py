from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

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
    company_id, title, original_url을 기준으로 유니크하게 관리됩니다.
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
    
    # 근무 조건 
    location: str = ""  # 근무지 주소
    job_type: str = ""  # 고용형태
    experience_level: str = ""  # 경력 요건
    education: str = ""  # 학력 요건
    work_shift: str = ""  # 근무시간
    conditions: WorkConditions = Field(default_factory=WorkConditions)  # 상세 근무조건
    
    # 급여 정보
    salary_text: str = ""  # 텍스트형 급여 정보
    salary: Dict[str, int] = Field(
        default_factory=lambda: {"min": 0, "max": 0}
    )
    
    # 직무 분야
    sector: str = ""  # 직무분야
    skills: List[str] = Field(default_factory=list)  # 기술 스택 목록
    
    # 채용 정보
    deadline: str = ""  # 마감일 텍스트
    deadline_timestamp: Optional[datetime] = None  # 파싱된 마감일
    total_count: int = 0  # 채용 인원
    
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
                "job_type": "정규직",
                "salary_text": "3,500~4,000만원",
                "sector": "웹개발",
                "total_count": 2,
                "original_url": "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=12345"
            }
        }