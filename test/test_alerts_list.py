import os

import pytest
from schema import SchemaError
from src.alerts import Alerts

config_file = 'test/alerts.yaml'
extra_alert_file = 'test/TST.yaml'
alerts_with_defaults = """  rules:
  - alert: zero
    expr: again_changed
    for: 10m
    labels:
      severity: WARN
    annotations:
      summary: some summary
      emailSubject: name_first
  - alert: one
    expr: ble
    for: 33m
    labels:
      severity: ERROR
    annotations:
      summary: something else
      emailSubject: 3rd
  - alert: two
    expr: some-other expression
    for: 2m # No value provided using default
    labels:
      severity: ERROR # No value provided using default
    annotations:
      summary: Triggerd by: some-other expression # No value provided using default
      emailSubject: Triggered by: some-other expression # No value provided using default"""

alerts_basic = """  rules:
  - alert: zero
    expr: test
    for: 2m
    labels:
      severity: WARN
    annotations:
      summary: some summary
      emailSubject: name_first
  - alert: one
    expr: ble
    for: 33m
    labels:
      severity: ERROR
    annotations:
      summary: something else
      emailSubject: 3rd"""



@pytest.fixture
def alerts():
    alerts = Alerts(filename=config_file)
    yield alerts


@pytest.fixture
def alerts_empty():
    alerts = Alerts()
    yield alerts

@pytest.fixture
def alerts_empty_files():
    alerts = Alerts()
    yield alerts
    os.remove('local_file')


def test_file_on_init(alerts):
    yaml = alerts.read_file(config_file)
    assert alerts.get_alerts() == yaml


def test_load_alerts_from_file(alerts_empty):
    yaml = Alerts.read_file(config_file)
    alerts_empty.read_alerts_from_file(config_file)
    assert yaml == alerts_empty.get_alerts()


def test_load_multiple_files(alerts_empty):
    alerts_empty.read_alerts_from_file(config_file)
    alerts_empty.read_alerts_from_file(extra_alert_file)
    assert alerts_with_defaults == alerts_empty.generate_alert_rules()


def test_generate_alert_rules(alerts):
    rules = alerts.generate_alert_rules()
    assert rules == alerts_basic


def test_default_values(alerts):
    alerts.read_alerts_from_file(extra_alert_file)
    rules = alerts.generate_alert_rules()
    assert rules == alerts_with_defaults


def test_fail_on_invalid_yaml(alerts_empty_files):
    invalid_yaml = """---
alerts:
  -
    name: 'zero'"""
    f = open(file='local_file', mode="w")
    f.write(invalid_yaml)
    f.close()
    with pytest.raises(SchemaError):
        alerts_empty_files.read_alerts_from_file('local_file')