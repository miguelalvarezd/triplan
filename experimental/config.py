class DevelopmentConfig():
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '1075'
    MYSQL_DB = 'db_triplan'


config = {
    'development': DevelopmentConfig
}
