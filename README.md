# 사람인 채용정보 API 서버

사람인 웹사이트의 채용공고를 크롤링하여 제공하는 RESTful API 서버입니다.

## 기능 소개

### 1. 채용정보 크롤링
- 사람인 웹사이트 채용공고 자동 수집
- 회사정보, 채용공고, 기술스택 등 데이터 구조화
- 중복 데이터 처리 및 정기적 업데이트

### 2. 회원 관리
- 회원가입/로그인
- JWT 기반 인증
- 회원정보 관리

### 3. 채용공고 관리
- 채용공고 목록/상세 조회
- 검색 및 필터링 (지역, 경력, 기술스택 등)
- 연관 채용공고 추천

### 4. 지원 관리
- 채용공고 지원
- 지원내역 관리
- 지원상태 추적

### 5. 북마크 기능
- 관심있는 채용공고 북마크
- 북마크 목록 관리
- 메모 및 태그 기능

## 기술 스택

- **Backend**: Node.js, Express.js
- **Database**: MongoDB
- **Authentication**: JWT
- **Documentation**: Swagger UI
- **Crawling**: Puppeteer
- **Logging**: Winston

## 설치 및 실행 방법

1. 저장소 클론
```bash
git clone [repository-url]
cd saramin-crawler
```

2. 환경변수 설정
```bash
cp .env.example .env
# .env 파일을 적절히 수정
```

3. 의존성 설치
```bash
npm install
```

4. 데이터베이스 실행
```bash
# MongoDB가 실행 중인지 확인
```

5. 서버 실행
```bash
# 개발 모드
npm run dev

# 프로덕션 모드
npm start
```

6. 크롤러 실행
```bash
npm run crawl
```

## API 문서

- Swagger UI: `http://localhost:3000/api-docs`

## API 엔드포인트

### Auth
- POST `/api/auth/register` - 회원가입
- POST `/api/auth/login` - 로그인
- GET `/api/auth/me` - 내 정보 조회

### Jobs
- GET `/api/jobs` - 채용공고 목록 조회
- GET `/api/jobs/:id` - 채용공고 상세 조회
- GET `/api/jobs/:id/related` - 연관 채용공고 조회

### Applications
- POST `/api/applications/jobs/:jobId` - 지원하기
- GET `/api/applications/me` - 내 지원내역 조회
- GET `/api/applications/:id` - 지원서 상세 조회

### Bookmarks
- POST `/api/bookmarks/jobs/:jobId` - 북마크 토글
- GET `/api/bookmarks` - 북마크 목록 조회
- PATCH `/api/bookmarks/:id/note` - 북마크 메모 수정

### Search
- GET `/api/search` - 통합 검색
- GET `/api/search/advanced` - 고급 검색
- GET `/api/search/suggestions` - 검색어 자동완성

## 환경변수 설정

```env
PORT=3000
MONGODB_URI=mongodb://localhost:27017/saramin_db
JWT_SECRET=your_jwt_secret
JWT_EXPIRES_IN=24h
NODE_ENV=development
```

## 데이터베이스 스키마

- User (사용자)
- Job (채용공고)
- Company (회사)
- Application (지원내역)
- Bookmark (북마크)
- Skill (기술스택)
- Category (직무카테고리)
- Log (시스템 로그)

## 오류 코드

| 코드 | 설명 |
|------|------|
| AUTH_FAILED | 인증 실패 |
| INVALID_TOKEN | 유효하지 않은 토큰 |
| NOT_FOUND | 리소스를 찾을 수 없음 |
| DUPLICATE_ENTRY | 중복된 데이터 |
| VALIDATION_ERROR | 유효성 검사 실패 |

## 작성자

이름: [김선강]
학번: [202011630]
이메일: [vnvndldl@naver.com]

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.