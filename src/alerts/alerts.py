import pkgutil
from pathlib import Path
from typing import Dict

from schema import Optional, Schema, SchemaError
from jinja2 import Template, TemplateError

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


class Alerts:
    ALERT_SCHEMA = Schema({
        'alerts':
            [
                {'name': str,
                 'expr': str,
                 Optional('for'): str,
                 Optional('severity'): str,
                 Optional('emailSubject'): str,
                 Optional('summary'): str

                 }
            ]
    })

    def __init__(self, filename: str = ''):
        self.__alerts = {}
        if Path(filename).is_file():
            self.read_alerts_from_file(filename)
            self.parse_alerts(self.__alerts)

    @staticmethod
    def read_file(filename: str) -> yaml:
        file = Path(filename)
        try:
            logger.info("Trying to open file: " + filename)
            f = open(file=file, encoding="utf-8")
            content = yaml.load(f, Loader=yaml.SafeLoader)
            logger.debug("Content :" + str(content))
            return content
        except FileNotFoundError as nff:
            logger.debug("Unable to open file")
            raise nff

    @staticmethod
    def parse_alerts(content, schema: Schema = ALERT_SCHEMA) -> Dict:
        try:
            schema.validate(content)
            logger.info("Content validated")
            return content
        except SchemaError as se:
            raise se

    def update_alert(self, position: int, alert: Dict):
        for key, value in alert.items():
            self.__alerts['alerts'][position][key] = value
        logger.debug('after: ' + str(self.__alerts['alerts'][position]))

    def upsert_alert(self, alerts: Dict):
        alerts_list = []
        for alert in self.__alerts['alerts']:
            alerts_list.append(alert['name'])

        for alert in alerts['alerts']:
            alert_name = alert['name']
            if alert_name in alerts_list:
                idx = alerts_list.index(alert_name)
                logger.debug('Found alert definition, position: ' + str(idx))
                logger.debug('now: ' + str(self.__alerts['alerts'][idx]))
                logger.debug('update: ' + str(alert))
                self.update_alert(position=idx, alert=alert)
            else:
                self.__alerts['alerts'].append(alert)
                alerts_list.append(alert['name'])

    def read_alerts_from_file(self, filename: str, schema: Schema = ALERT_SCHEMA):
        read_alerts = self.parse_alerts(self.read_file(filename), schema)
        if len(self.__alerts) == 0:
            self.__alerts = read_alerts
        else:
            self.upsert_alert(alerts=read_alerts)

    def get_alerts(self) -> Dict:
        return self.__alerts

    def generate_alert_rules(self) -> str:
        try:
            template_file = pkgutil.get_data(__name__, 'templates/alert_rules.j2').decode('utf-8')
            jinja2_template = Template(template_file)
            output = jinja2_template.render(self.__alerts)
            logger.debug('Generated output:')
            logger.debug(output)
            return str(output)
        except TemplateError as error:
            logger.error("Failed to render template")
            logger.error(error)
            raise error

    def write_alert_rules(self, filename):
        output = self.generate_alert_rules()
        f = open(file=filename, encoding='utf-8', mode="w")
        f.write(output)
        f.close()