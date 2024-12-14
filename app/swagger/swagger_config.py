from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# Swagger 설정
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swagger_config = {
    'app_name': "Job Portal API Documentation",
    'dom_id': '#swagger-ui',
    'deepLinking': True,
    'layout': 'BaseLayout',
    'validatorUrl': None,
    'displayRequestDuration': True,
    'docExpansion': 'none',
    'defaultModelsExpandDepth': 3,
    'defaultModelExpandDepth': 3,
    'supportedSubmitMethods': ['get', 'post', 'put', 'delete'],
    'operationsSorter': 'alpha',
    
    # JWT 인증을 위한 설정 추가
    'securityDefinitions': {
        'bearerAuth': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"'
        }
    },
    'security': [{'bearerAuth': []}]
}

# Swagger UI blueprint 등록
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config=swagger_config,
    # OAuth 설정 추가
    oauth_config={
        'clientId': "swagger-ui",
        'clientSecret': "swagger-ui-secret",
        'realm': "swagger-ui-realm",
    }
)

# CORS 설정 추가
@swagger_ui_blueprint.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE'
    return response

app.register_blueprint(swagger_ui_blueprint)

# swagger.json 파일 제공을 위한 라우트
@app.route('/static/swagger.json')
def serve_swagger_spec():
    return send_from_directory('static', 'swagger.json')

# 에러 핸들러 추가
@app.errorhandler(404)
def not_found_error(error):
    return {
        'status': 'error',
        'message': 'The requested URL was not found on the server.'
    }, 404

@app.errorhandler(500)
def internal_error(error):
    return {
        'status': 'error',
        'message': 'An internal server error occurred.'
    }, 500