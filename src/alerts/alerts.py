from pathlib import Path
from typing import Dict
from schema import Optional, Schema, SchemaError, Or

import yaml
import logging


def extract_alerts(content):
    return content['alerts']


console_formatter = logging.Formatter('%(levelname)s:%(message)s')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(console_formatter)

logger = logging.getLogger(__name__)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

alert_schema = Schema({
    'name': str,
    'expr': str,
    'for': str,
    'subjectEmail': str,
})

custom_alert_schema = Schema({
    'name': str,
    Optional('expr'): str,
    Optional('for'): str
})

config_file_schema = Schema({
    'alerts': {
        'defaults': [
            alert_schema
        ],
        'custom_alerts': {
            'environment': {
                Or('prd','acc', 'tst', 'sbx'):
                    [
                        custom_alert_schema]
            },
            'cluster': {
                "1_tst":
                    [
                        custom_alert_schema
                    ]
            }

        }
    }

})


class Alerts:
    YAML_CUSTOM_CONF_PREFIX = 'custom_alerts'
    YAML_ALERTS_PREFIX = 'alerts'

    def __init__(self, path: str = "null"):
        self.__alert_names = []
        self.__alerts = []
        self.__configuration = {}
        self.__path: Path = Path('')
        self.__set_file_path(path)
        content = self.parse_alert_file()
        self.__configuration = content

    def __set_file_path(self, filename: str) -> None:
        logger.debug("Name of file: " + filename)
        path = Path(filename)
        logger.debug("CWD: " + str(path.cwd()))
        logger.debug("Does file exist: " + str(path.exists()))
        if path.is_file():
            self.__path = Path(path)
        else:
            logger.error("File not found, therefore not set")
            raise FileNotFoundError

    def get_file_path(self) -> str:
        return str(self.__path)

    def add_alert_def(self, alert: Dict):
        alerts = {}
        name = alert['name']
        expr = alert['expr']
        alerts['name'] = name
        alerts['expr'] = expr
        self.__alert_names.append(name)
        self.__alerts.append(alerts)

    def len_alerts(self):
        return len(self.__prep_alerts)

    def parse_alert_file(self) -> Dict:
        f = open(file=self.__path, encoding="utf-8")
        content = yaml.load(f, Loader=yaml.SafeLoader)
        logger.debug("Content :" + str(content))
        return content

    def get_all_alerts(self):
        print(self.__alerts)

    def get_custom_configuration(self):
        return self.__configuration['alerts'][self.YAML_CUSTOM_CONF_PREFIX]

    def get_default_alerts(self):
        return self.__configuration['alerts']['defaults']

    def get_custom_env_alerts(self, environment=None):
        try:
            alerts = self.__configuration['alerts'][self.YAML_CUSTOM_CONF_PREFIX]['environment'][environment]
        except KeyError:
            logger.info("Custom alerts for environment: " + environment + " not found")
            alerts = None
        return alerts

    def get_custom_cluster_alerts(self, cluster=None):
        try:
            alerts = self.__configuration['alerts'][self.YAML_CUSTOM_CONF_PREFIX]['cluster'][cluster]
        except KeyError:
            logger.info("Custom alerts for cluster: " + cluster + " not found")
            alerts = None
        return alerts

    def get_alert(self, name):
        index = self.__alert_names.index(name)
        return self.__alerts[index]

    def count_alerts(self) -> int:
        return len(self.__alerts)
