from flask import jsonify
from .custom_errors import CustomError, AuthenticationError, DataFormatError

def init_error_handlers(app):
    """글로벌 에러 핸들러 등록"""
    
    @app.errorhandler(CustomError)
    def handle_custom_error(error):
        return jsonify({
            'status': 'error',
            'message': error.message,
            'code': error.code
        }), 400

    @app.errorhandler(AuthenticationError)
    def handle_auth_error(error):
        return jsonify({
            'status': 'error',
            'message': error.message,
            'code': error.code
        }), 401

    @app.errorhandler(DataFormatError)
    def handle_format_error(error):
        return jsonify({
            'status': 'error',
            'message': error.message,
            'code': error.code
        }), 400