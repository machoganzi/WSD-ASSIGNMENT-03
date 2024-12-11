# WSD-Assignment-03

## 빌드를 위한 명령어

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. MongoDB 연결 설정 (`config.py`)
```python
MONGODB_URI = "YOUR_MONGODB_URI"
DATABASE_NAME = "YOUR_DB_NAME"
```

### 3. 서버 실행
```bash
python main.py
```

### 4. 크롤러 실행 (100개 이상의 데이터 수집)
```bash
python run_crawler.py
```

---

## 프로젝트 구조

```
project/
├── app/
│   ├── crawlers/           # 크롤링 관련
│   │   ├── __init__.py
│   │   ├── saramin_crawler.py
│   │   └── test.py
│   ├── models/            # 데이터베이스 모델
│   │   ├── init_db.py
│   │   └── schemas.py
│   ├── routes/            # API 라우트
│   │   ├── auth_routes.py
│   │   ├── job_routes.py
│   │   ├── application_routes.py
│   │   └── bookmark_routes.py
│   ├── services/          # 비즈니스 로직
│   │   ├── auth_service.py
│   │   ├── job_service.py
│   │   ├── application_service.py
│   │   └── bookmark_service.py
│   ├── utils/             # 유틸리티
│   │   └── auth_utils.py
│   ├── errors/            # 에러 처리
│   │   ├── custom_errors.py
│   │   └── error_handler.py
│   └── static/            # Swagger 문서
│       └── swagger.json
├── config.py              # 설정 파일
├── requirements.txt       # 패키지 의존성
└── main.py                # 앱 진입점
```

---

## API 문서

- **Swagger UI**: [http://localhost:5000/api/docs](http://localhost:5000/api/docs)
- 전체 API 명세는 `/static/swagger.json`에서 확인 가능

---

## 주요 기능

### 1. **회원 관리 API** (`/auth`)
- 회원 가입/로그인
- JWT 토큰 기반 인증
- 프로필 수정

### 2. **채용공고 API** (`/jobs`)
- 목록 조회 (페이지네이션)
- 검색 및 필터링
- 상세 조회

### 3. **지원 관리 API** (`/applications`)
- 지원하기
- 지원 취소
- 지원 내역 조회

### 4. **북마크 API** (`/bookmarks`)
- 북마크 추가/제거
- 북마크 목록 조회

