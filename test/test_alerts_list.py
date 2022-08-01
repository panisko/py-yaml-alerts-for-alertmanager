import pytest

from src.alerts import Alerts

config_file = 'alerts.yaml'


@pytest.fixture
def alerts():
    alerts = Alerts(path=config_file)
    yield alerts


def test_alert_class_is_created(alerts):
    # assert type(alerts) != str('<class \'src.alerts.alerts.Alerts\'>')
    pass


def test_get_alert_file(alerts):
    assert alerts.get_file_path() == config_file


# def test_parse_alert_file(alerts):
#     alerts.parse_alert_file()
#     assert alerts.count_alerts() == 1


def test_custom_alerts_env_not_found(alerts):
    assert alerts.get_custom_env_alerts("tst") is None


def test_custom_alerts_cluster_not_found(alerts):
    assert alerts.get_custom_cluster_alerts("none_existing") is None


def test_list_alert(alerts):
    alerts.get_all_alerts()
    # print(alerts.get_custom_configuration())
    # print(alerts.get_default_alerts())
    print(alerts.get_custom_env_alerts("prd"))
    # print(alerts.get_custom_cluster_alerts("1_tst"))
    pass


def test_add_alert_definition(alerts):
    alert = {
        'name': 'alert3',
        'expr': 'test'
    }
    alerts.add_alert_def(alert)
    assert alerts.get_alert('alert3') == alert
