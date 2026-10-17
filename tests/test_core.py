import csv
import json
import subprocess
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from n2_collector.collector import collect, identify_product, license_rows, INVENTORY, IDENTITIES
from n2_collector.model import Report, UNKNOWN
from n2_collector.reporting import export_csv, safe_cell
from n2_collector.transport import load_transport, DeliveryError

class Registry:
    def __init__(self, installed=True):
        self.installed = installed
    def values(self, hive, path, names):
        if path == INVENTORY and self.installed:
            return [{'OfficeProductReleaseIds': 'O365ProPlusRetail,ProPlus2024Volume', 'OfficePackageVersion': '16.0.123'}]
        if path.startswith(IDENTITIES) and self.installed:
            return [{'EmailAddress': 'pessoa@example.com'}]
        return []
    def subkeys(self, hive, path):
        return ['conta'] if path == IDENTITIES and self.installed else []

def query(script):
    if 'Win32_ComputerSystem' in script:
        return {'hostname': 'PC-01', 'username': 'ACIJ\\colaborador', 'domain': 'ACIJ', 'windows': 'Windows 11 Pro'}
    return [{'name': 'Office LTSC 2024', 'description': 'VOLUME_KMSCLIENT', 'status': 1}]

def test_full_collection():
    progress = []
    report = collect(progress.append, registry=Registry(), query=query, system='Windows')
    assert report.hostname == 'PC-01'
    assert 'Microsoft 365' in report.office and 'Office 2024' in report.office
    assert report.office_email == 'pessoa@example.com'
    assert 'Licenciado' in report.activation and 'Volume KMS' in report.license_type
    assert len(progress) == 4

def test_office_year():
    for year in ['2016', '2019', '2021', '2024']:
        assert f'Office {year}' in identify_product(f'ProPlus{year}Volume')

def test_no_guess_from_internal_version():
    assert 'não identificado' in identify_product('Office16')

def test_absence_and_unavailable_fields():
    report = collect(registry=Registry(False), query=lambda _: {}, system='Windows')
    assert report.office == report.office_email == UNKNOWN
    assert report.activation == UNKNOWN

def test_failures_are_partial():
    def timeout(_):
        raise subprocess.TimeoutExpired('powershell', 35)
    report = collect(registry=Registry(), query=timeout, system='Windows')
    assert report.hostname == UNKNOWN and 'Microsoft 365' in report.office
    assert report.office_email == 'pessoa@example.com'

def test_non_windows_does_not_query():
    def forbidden(_):
        raise AssertionError('consulta indevida')
    assert collect(query=forbidden, system='Linux').hostname == UNKNOWN

def test_product_statuses_remain_separate():
    status, _ = license_rows([{'name': 'Visio', 'status': 1}, {'name': 'Office', 'status': 0}])
    assert 'Visio: Licenciado' in status and 'Office: Não licenciado' in status

def test_csv_injection():
    for value in ['=1+1', '+cmd', '-1', '@SUM(A1)', '  =1', '\tfoo']:
        assert safe_cell(value).startswith("'")

def test_export(tmp_path):
    path = tmp_path / 'relatorio.csv'
    export_csv(Report(hostname='=formula;á\nlinha'), path)
    with path.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.reader(stream, delimiter=';'))
    assert rows[1] == ['Computador', "'=formula;á\nlinha"]

def test_simulation_without_network(tmp_path):
    import socket
    def forbidden(*a, **kw):
        raise AssertionError('Rede proibida')
    with patch.object(socket, 'socket', forbidden):
        result = load_transport(tmp_path / 'absent.json').send(Report())
    assert result.simulated and 'Nenhum dado enviado' in result.message

def test_invalid_config_fails_closed(tmp_path):
    for content in ['{', '[]', '{"mode":"smtp"}', '{"mode":"test","password":"secret"}']:
        path = tmp_path / 'config.json'
        path.write_text(content)
        with unittest.TestCase().assertRaises(DeliveryError):
            load_transport(path)


def test_valid_config(tmp_path):
    path = tmp_path / 'config.json'
    path.write_text(json.dumps({'mode': 'test'}))
    assert load_transport(path).send(Report()).simulated

def test_subject_date():
    assert Report(hostname='PC', collected_at='2026-10-14T12:00:00-03:00').subject == 'Coletor | PC | 2026-10-14'


class CoreTests(unittest.TestCase):
    """Adapta cenários de domínio para execução sem dependências externas."""


def _adapt(fn):
    def run(self):
        if fn.__code__.co_argcount:
            with tempfile.TemporaryDirectory() as directory:
                fn(Path(directory))
        else:
            fn()
    return run

for _name, _fn in list(globals().items()):
    if _name.startswith('test_') and callable(_fn):
        setattr(CoreTests, _name, _adapt(_fn))
        del globals()[_name]

if __name__ == '__main__':
    unittest.main()
