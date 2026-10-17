"""Orquestra coleta; falhas parciais preservam os demais resultados."""
import platform
import re
from collections.abc import Callable
from .model import Report, UNKNOWN
from .windows import Registry, powershell, SYSTEM_SCRIPT, LICENSE_SCRIPT

INVENTORY = r"SOFTWARE\Microsoft\Office\ClickToRun\Inventory\Office\16.0"
IDENTITIES = r"SOFTWARE\Microsoft\Office\16.0\Common\Identity\Identities"
UNINSTALL = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
STATUS = {0: "Não licenciado", 1: "Licenciado", 2: "Período de tolerância inicial", 3: "Tolerância adicional", 4: "Tolerância não original", 5: "Notificação", 6: "Tolerância estendida"}

def identify_product(product: str) -> str:
    lower = product.lower()
    if lower.startswith(('o365', 'm365')):
        return f"Microsoft 365 ({product})"
    for year in ('2024', '2021', '2019', '2016'):
        if year in product:
            return f"Office {year} ({product})"
    return f"{product} — edição/ano não identificado"

def license_rows(records: list[dict]) -> tuple[str, str]:
    # Cada status permanece associado ao produto. Nunca mistura licença de Visio com Word.
    statuses, types = [], []
    for row in records:
        if not isinstance(row, dict) or not row.get('name'):
            continue
        name = str(row.get('name') or UNKNOWN)
        statuses.append(f"{name}: {STATUS.get(row.get('status'), UNKNOWN)}")
        description = str(row.get('description', '')).upper()
        kind = next((label for marker, label in [('VOLUME_KMSCLIENT', 'Volume KMS'), ('VOLUME_MAK', 'Volume MAK'), ('RETAIL', 'Varejo')] if marker in description), UNKNOWN)
        types.append(f"{name}: {kind}")
    return '; '.join(statuses) or UNKNOWN, '; '.join(types) or UNKNOWN

def collect(progress: Callable[[str], None] = lambda _: None, *, registry=None, query=powershell, system=None) -> Report:
    report = Report()
    if (system or platform.system()) != 'Windows':
        report.notes.append('Coleta disponível apenas no Windows 10/11; nenhum dado coletado neste sistema.')
        return report
    registry = registry or Registry()
    progress('Consultando computador e Windows…')
    try:
        data = query(SYSTEM_SCRIPT)
        for name in ('hostname', 'username', 'domain', 'windows'):
            value = data.get(name)
            if isinstance(value, str) and value.strip():
                setattr(report, name, value)
    except Exception:
        report.notes.append('Consulta do Windows indisponível ou bloqueada; consulte a TI.')
    progress('Identificando Office…')
    try:
        products = []
        for row in registry.values('HKEY_LOCAL_MACHINE', INVENTORY, ('OfficeProductReleaseIds', 'OfficePackageVersion')):
            for product in re.split('[,;]', row.get('OfficeProductReleaseIds', '')):
                if product.strip():
                    products.append(identify_product(product.strip()) + ' | build ' + row.get('OfficePackageVersion', UNKNOWN))
        # MSI e instalações antigas: somente nomes explícitos de produtos Office.
        for key in registry.subkeys('HKEY_LOCAL_MACHINE', UNINSTALL):
            for row in registry.values('HKEY_LOCAL_MACHINE', UNINSTALL + '\\' + key, ('DisplayName',)):
                name = row.get('DisplayName', '')
                if re.search(r'Microsoft (?:Office|365)', name, re.I) and re.search(r'2016|2019|2021|2024|365', name):
                    products.append(name)
        report.office = '; '.join(dict.fromkeys(products)) or UNKNOWN
        if not products:
            report.notes.append('Office ausente ou instalação não identificável pelas fontes consultadas.')
        else:
            report.notes.append('Fonte Office: inventário Click-to-Run e nomes de desinstalação; entradas residuais podem existir.')
    except Exception:
        report.notes.append('Consulta do inventário Office parcial ou bloqueada.')
    progress('Consultando licenciamento Office…')
    try:
        records = query(LICENSE_SCRIPT)
        report.activation, report.license_type = license_rows(records if isinstance(records, list) else [records])
    except Exception:
        report.notes.append('Consulta de licenciamento indisponível ou bloqueada.')
    report.notes.append('Licenciamento consultado via CIM/Office SPP por produto; não comprova ativação moderna Microsoft 365. Ausência de resultado não significa Office desativado.')
    progress('Verificando identidade local do Office…')
    try:
        emails = []
        for key in registry.subkeys('HKEY_CURRENT_USER', IDENTITIES):
            for row in registry.values('HKEY_CURRENT_USER', IDENTITIES + '\\' + key, ('EmailAddress',)):
                value = row.get('EmailAddress', '')
                if re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value):
                    emails.append(value)
        report.office_email = '; '.join(sorted(set(emails))) or UNKNOWN
        if emails:
            report.notes.append('E-mail proveniente de identidade local Office; pode estar em cache e não confirma sessão ativa. Múltiplas identidades são apresentadas sem escolher uma conta.')
    except Exception:
        report.notes.append('E-mail Office indisponível ou acesso negado.')
    return report
