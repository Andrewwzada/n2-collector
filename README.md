# Coletor

Aplicativo Python/PySide6 para inventário técnico voluntário em Windows 10/11. **Versão inicial em modo de testes: nenhum e-mail é enviado.** Não requer administrador para operar; políticas locais podem impedir consultas, que serão indicadas como indisponíveis.

## Arquitetura e etapas implementadas

1. `model.py`: relatório tipado, data com fuso e assunto.
2. `windows.py` e `collector.py`: consultas somente de leitura, tempo limite, identificação conservadora e falhas parciais.
3. `transport.py`: contrato `Transport`, configuração validada e transporte simulado sem rede ou persistência.
4. `app.py`: interface PySide6, coleta em tarefa vinculada à janela para manter a interface responsiva, execução exclusivamente após clique; nenhum serviço, agendamento ou coleta oculta.
5. `reporting.py`: utilitário CSV preservado internamente; sem botão de exportação na interface.
6. `tests/`, `scripts/build.ps1` e documentação de homologação/distribuição.

## Preparar no Windows

Use Python 3.11 ou superior, 64 bits, instalado para seu usuário, em uma pasta de desenvolvimento local. Os comandos abaixo criam apenas o ambiente do projeto e instalam suas dependências. Não são necessários nos computadores dos colaboradores.

```powershell
cd C:\Projeto\n2-collector
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m n2_collector
```

Se usar outra versão instalada do Python, ajuste `-3.12`. Não é preciso ativar a venv nem mudar a política de execução do PowerShell.

## Gerar o executável

Execute `scripts/build.ps1` no Windows se a política da organização permitir scripts. O build deve acontecer no Windows: WSL, Ubuntu e Docker Linux não geram este executável Windows com PyInstaller.

Alternativa manual, sem alterar a política de scripts:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
# Prossiga somente se os testes passarem.
.\.venv\Scripts\python.exe scripts/prepare_branding.py
if ($LASTEXITCODE -ne 0) { throw "Falha ao preparar ícone" }
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean N2Collector.spec
if ($LASTEXITCODE -ne 0) { throw "Falha na compilação" }
Copy-Item config.json dist/config.json
Get-FileHash dist/Coletor.exe -Algorithm SHA256
```

Saída: `dist\Coletor.exe` e `dist\config.json`. Python e Qt ficam no pacote. O modo onefile extrai bibliotecas em uma pasta temporária durante a execução; isso não altera configurações do Windows. O binário ainda precisa de homologação Windows e assinatura corporativa antes de distribuição ampla.

## Configuração e uso

`config.json`, ao lado do `.exe` (ou na raiz em desenvolvimento):

```json
{"mode": "test"}
```

Arquivo ausente também resulta em teste. Configurações inválidas ou modos diferentes falham sem enviar. Não coloque credenciais nesse arquivo. O destinatário previsto é `andrew@soutechgroup.com`; assunto: `Coletor | COMPUTADOR | AAAA-MM-DD`.

O colaborador abre o aplicativo, lê o aviso, clica **Enviar para Andrew**, acompanha a coleta e vê **Simulação concluída. Nenhum dado enviado**. O relatório permanece somente em memória, com rolagem na própria janela; não há logs com dados coletados nem envio ao fechar.

## Distribuição na pasta compartilhada ACIJ

Após homologação e aprovação da TI, publique os dois arquivos em pasta com leitura/execução para colaboradores e escrita apenas para responsáveis pela distribuição. Exemplo: `\\servidor\TI\Coletor\Coletor.exe`. Mantenha versões anteriores em local restrito e publique atualizações quando ninguém estiver usando o executável.

Teste execução a partir do caminho UNC e, se houver indisponibilidade da rede, distribua cópia local aprovada com hash validado. Compartilhamento desconectado pode impedir a abertura; a coleta local já aberta não depende de rede neste modo.

Assine o executável com certificado de assinatura de código da organização e valide assinatura/hash após publicação. SmartScreen, Defender, AppLocker e WDAC podem exigir análise e liberação pela TI conforme política corporativa. **Não desative antivírus nem contorne proteções**. A reputação SmartScreen pode continuar exigindo análise mesmo com assinatura.

## Desenvolvimento e validação em Ubuntu/WSL

Os testes de domínio não precisam de PySide6, de Windows nem de dependências externas:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 -m compileall -q src scripts
```

A interface exige PySide6 e ambiente gráfico. Os testes usam fontes Windows simuladas; não substituem testes no Windows real. Veja [homologação](docs/HOMOLOGACAO.md) e [limitações e transporte futuro](docs/TECNICO.md).

## Identidade SOUTECHGROUP

Janela compacta (550 × 420 unidades lógicas, com escala automática do Qt), logo centralizada de 140 pixels lógicos e relatório com rolagem. O PNG original é preservado e sua cópia é incluída no pacote Python e no executável. A interface remove apenas o fundo branco em memória; o ícone é gerado com a mesma transparência. Não depende do PNG externo nos computadores de destino.

Para recompilar no PowerShell, na raiz do projeto, sem alterar políticas de execução:

```powershell
Set-Location C:\Projeto\n2-collector
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw "Testes falharam" }
.\.venv\Scripts\python.exe scripts/prepare_branding.py
if ($LASTEXITCODE -ne 0) { throw "Falha ao preparar ícone" }
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean N2Collector.spec
if ($LASTEXITCODE -ne 0) { throw "Falha na compilação" }
Copy-Item config.json dist/config.json
```
