import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_PARENT = os.path.dirname(PROJECT_ROOT)
config_file = os.path.join(PROJECT_ROOT, 'config.json')

class ConfigManager(object):

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
                'name': 'db.sqlite',
                'host': 'localhost',
                'user': '',
                'password': '',
                'port': '',
                'type': 'sqlite'
            },
            'system': {
                'version': '1.0.0',
                'name': 'viLogged Visitor Management System',
                'lastUpdate': ''
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
        if config['database']['type'] == 'sqlite':
            name = config['database']['name']
            config['database']['name'] = os.path.join(PROJECT_ROOT, name)
            config['database']['engine'] = 'django.db.backends.sqlite3'

        if config['database']['type'] == 'mssql':
            config['engine'] = 'sqlserver_ado'

        return config['database']

    def set_config(self, config_data, type):
        config = self.get_config()
        config[type] = config_data
        ConfigManager.create_config(config)
