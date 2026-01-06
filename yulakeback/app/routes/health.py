"""
健康檢查 API
"""
from flask_restx import Namespace, Resource

health_ns = Namespace('health', description='健康檢查')


@health_ns.route('/health')
class Health(Resource):
    @health_ns.doc('health_check')
    def get(self):
        """健康檢查"""
        return {'status': 'healthy', 'service': 'yulake-api'}


@health_ns.route('/')
class Root(Resource):
    @health_ns.doc('root')
    def get(self):
        """API 根路徑"""
        return {
            'message': 'Yulake API is running',
            'version': '1.0',
            'docs': '/docs'
        }
