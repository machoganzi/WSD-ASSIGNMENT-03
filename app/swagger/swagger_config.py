from flask_swagger_ui import get_swaggerui_blueprint

# Swagger UI 웹 경로 및 JSON 파일 경로 설정
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

# Swagger UI 설정
swagger_config = {
    'app_name': "Job Portal API Documentation",
    'dom_id': '#swagger-ui',
    'deepLinking': True,  # URL에 API 위치 정보 포함
    'layout': 'BaseLayout',
    'validatorUrl': None,
    'displayRequestDuration': True,  # 요청 수행 시간 표시
    'docExpansion': 'none',  # 기본적으로 API 목록 접기
    'defaultModelsExpandDepth': 3,  # 모델 상세 정보 표시 깊이
    'defaultModelExpandDepth': 3,
    'supportedSubmitMethods': ['get', 'post', 'put', 'delete'],  # 지원하는 HTTP 메서드
    'operationsSorter': 'alpha'  # API 알파벳 순 정렬
}

# Swagger UI blueprint 생성
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config=swagger_config
)