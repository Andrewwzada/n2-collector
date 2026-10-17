"""Consultas Windows delimitadas; nenhuma gravação no Registro ou elevação."""
import json
import os
import subprocess
from pathlib import Path

# Script constante: não recebe nem interpola dados do usuário.
SYSTEM_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$c = Get-CimInstance Win32_ComputerSystem -OperationTimeoutSec 10
$o = Get-CimInstance Win32_OperatingSystem -OperationTimeoutSec 10
[pscustomobject]@{hostname=$c.Name;username=$c.UserName;domain=$(if($c.PartOfDomain){$c.Domain}else{'Não se aplica (grupo de trabalho)'});windows=($o.Caption+' | versão '+$o.Version+' | build '+$o.BuildNumber)} | ConvertTo-Json -Compress
"""
LICENSE_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
@(Get-CimInstance SoftwareLicensingProduct -Filter "ApplicationID='0ff1ce15-a989-479d-af46-f275c6370663'" -OperationTimeoutSec 10 | Where-Object { $_.PartialProductKey } | ForEach-Object { [pscustomobject]@{name=$_.Name;description=$_.Description;status=[int]$_.LicenseStatus} }) | ConvertTo-Json -Compress
"""

def powershell(script: str):
    executable = Path(os.environ.get("SystemRoot", r"C:\Windows")) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    result = subprocess.run([str(executable), '-NoLogo', '-NoProfile', '-NonInteractive', '-Command', script],
                            capture_output=True, timeout=35, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), check=True)
    return json.loads(result.stdout.decode('utf-8-sig').strip() or '[]')

class Registry:
    """Lê apenas valores solicitados; não enumera dados de autenticação."""
    def values(self, hive: str, path: str, names: tuple[str, ...]) -> list[dict]:
        import winreg
        results = []
        for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
            try:
                with winreg.OpenKey(getattr(winreg, hive), path, 0, winreg.KEY_READ | view) as key:
                    record = {}
                    for name in names:
                        try:
                            value = winreg.QueryValueEx(key, name)[0]
                            if isinstance(value, (str, list)):
                                record[name] = ','.join(value) if isinstance(value, list) else value
                        except OSError:
                            pass
                    if record and record not in results:
                        results.append(record)
            except FileNotFoundError:
                pass
        return results

    def subkeys(self, hive: str, path: str) -> list[str]:
        import winreg
        results = []
        for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
            try:
                with winreg.OpenKey(getattr(winreg, hive), path, 0, winreg.KEY_READ | view) as key:
                    for index in range(winreg.QueryInfoKey(key)[0]):
                        name = winreg.EnumKey(key, index)
                        if name not in results:
                            results.append(name)
            except FileNotFoundError:
                pass
        return results
