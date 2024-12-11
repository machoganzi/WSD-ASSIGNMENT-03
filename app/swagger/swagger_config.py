from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'  # Swagger UI 웹 경로
API_URL = '/static/swagger.json'  # Swagger JSON 파일 경로

# Swagger UI blueprint 설정
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Job Portal API Documentation"
    }
)