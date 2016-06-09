import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_PARENT = os.path.dirname(PROJECT_ROOT)
config_file = os.path.join(PROJECT_ROOT, 'local_assets/config.json')

class ConfigManager(object):

    @classmethod
    def get_db_engine(cls, type):
        stack = dict(
            sqlite='django.db.backends.sqlite3',
            mysql='django.db.backends.mysql',
            postgres='django.db.backends.postgresql_psycopg2',
            mssql='sqlserver'
        )
        return stack.get(type)

    @staticmethod
    def default_config():
        return {
            'authSource': 'api',
            'ldap': {
                'host': '',
                'user': '',
                'password': '',
                'port': '',
                'baseDN': ''
            },
            'database': {
                'name': 'local_assets/db.sqlite',
                'host': 'localhost',
                'user': '',
                'password': '',
                'port': '',
                'type': 'sqlite'
            },
            'system': {
                'version': '1.0.0',
                'name': 'viLogged Visitor Management System',
                'lastUpdate': '',
                'db_source': 'environment'
            }
        }

    def get_config(self, type=None):
        if os.path.isfile(config_file):
            config = open(config_file).read()
            config = json.loads(config)
        else:
            config = ConfigManager.default_config()
            self.create_config(config)

        if type == 'database':
            return self._get_db_config(config)
        if type is None:
            return config
        try:
            return config[type]
        except KeyError:
            config[type] = {}

        return config[type]

    @staticmethod
    def create_config(config):
        with open(config_file, 'w') as outfile:
            json.dump(config, outfile, sort_keys = True, indent = 2, ensure_ascii=False)

    def _get_db_config(self, config):
        db_type = config['database']['type']
        db_engine = self.get_db_engine(db_type)
        if db_type == 'sqlite' or db_engine is None:
            name = config['database'].get('name', '/local_assets/db.sqlite')
            config['database']['name'] = os.path.join(PROJECT_ROOT, name)
            config['database']['engine'] = db_engine
        else:
            config['database']['engine'] = db_engine

        if db_type == 'mssql':
            config['database']['options'] = {
                'provider': 'SQLNCLI11',
                # 'extra_params': 'DataTypeCompatibility=80;MARS Connection=True;',
                'use_legacy_date_fields': False,
            }
        system = config.get('system', {})
        return self.set_environment(config['database'], system.get('db_source'))

    def set_config(self, config_data, type):
        config = self.get_config()
        config[type] = config_data
        ConfigManager.create_config(config)

    def set_environment(self, db_config, use_env):
        if use_env and os.environ.get('DB_NAME'):
            db_config['name'] = os.environ.get('DB_NAME')
            db_config['engine'] = os.environ.get('DB_ENGINE')
            db_config['password'] = os.environ.get('DB_PASSWORD')
            db_config['host'] = os.environ.get('DB_HOST')
            db_config['user'] = os.environ.get('DB_USER')
            if db_config.get('options'):
                db_config['options'] = os.environ.get('DB_OPTIONS', dict())
            if db_config.get('port'):
                db_config['port'] = os.environ.get('DB_PORT', '')
        return db_config
