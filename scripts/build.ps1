# Executar manualmente no PowerShell Windows, na raiz do projeto.
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'O build deve ser executado no Windows.' }
Set-Location (Join-Path $PSScriptRoot '..')
$Python = Join-Path (Get-Location) '.venv\Scripts\python.exe'
if (!(Test-Path $Python)) { throw 'Crie .venv e instale .[dev] conforme README.md.' }
& $Python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Testes falharam.' }
& $Python scripts/prepare_branding.py
if ($LASTEXITCODE -ne 0) { throw 'Preparação da logo falhou.' }
& $Python -m PyInstaller --noconfirm --clean N2Collector.spec
if ($LASTEXITCODE -ne 0) { throw 'Build falhou.' }
Copy-Item config.json dist/config.json
Get-FileHash dist/Coletor.exe -Algorithm SHA256 | Format-List
