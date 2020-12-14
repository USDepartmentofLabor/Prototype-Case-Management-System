import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'hard to guess string'
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 900))
    JWT_BLACKLIST_ENABLED = os.environ.get('JWT_BLACKLIST_ENABLED', 'true').lower() in ['true', 'on', '1']
    JWT_BLACKLIST_TOKEN_CHECKS = os.environ.get('JWT_BLACKLIST_TOKEN_CHECKS', 'access,refresh').split(",")
    JWT_ERROR_MESSAGE_KEY = 'message'
    WEB_APP_URL = os.environ.get('WEB_APP_URL', 'http://localhost:4200')

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'email-smtp.us-east-1.amazonaws.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = os.environ.get('MAIL_SUBJECT_PREFIX')
    MAIL_SENDER = os.environ.get('MAIL_SENDER')

    METABASE_URL = os.environ.get('METABASE_URL', 'http://localhost:3000')
    METABASE_USERNAME = os.environ.get('METABASE_USERNAME', None)
    METABASE_PASSWORD = os.environ.get('METABASE_PASSWORD', None)
    METABASE_AUTH_ID = os.environ.get('METABASE_AUTH_ID', None)
    METABASE_DB = os.environ.get('METABASE_DB', 0)
    METABASE_SECRET_KEY = os.environ.get('METABASE_SECRET_KEY', 'hard to guess string')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

    STORAGE_PROVIDER = os.environ.get('STORAGE_PROVIDER', 'LOCAL')
    STORAGE_KEY = os.environ.get('STORAGE_KEY')
    STORAGE_SECRET = os.environ.get('STORAGE_SECRET')
    STORAGE_CONTAINER = os.environ.get('STORAGE_CONTAINER', '/tmp')
    STORAGE_ALLOWED_EXTENSIONS = os.environ.get('STORAGE_ALLOWED_EXTENSIONS',
                                                'txt,doc,docx,xls,xlsx,pdf,png,jpg,jpeg,md').split(',')
    STORAGE_SERVER = True
    STORAGE_SERVER_URL = '/files'

    DATA_DB_URI = os.environ.get(
        'DATA_DB_URI', 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    )
    DATA_DB = os.environ.get('DATA_DB', 'data_pg')

    BABEL_TRANSLATION_DIRECTORIES = '../translations'

    API_VERSION = '0.26.0'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'eps-api-dev.sqlite')
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'eps-api-test.sqlite')
    )
    BCRYPT_LOG_ROUNDS = 4
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'PROD_DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'eps-api.sqlite')
    )
    STORAGE_PROVIDER = os.environ.get('STORAGE_PROVIDER', 'S3')
    STORAGE_SERVER = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
