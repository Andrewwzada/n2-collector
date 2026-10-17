# Fontes, limitações e evolução

## Windows e Office

- Windows: PowerShell Windows com caminho de sistema, `-NoProfile -NonInteractive`, CIM `Win32_ComputerSystem` e `Win32_OperatingSystem`. Usuário vem de `UserName`, não do usuário que iniciou o processo elevado. Sessões RDP/múltiplas podem não corresponder ao colaborador; valor indisponível permanece “Não identificado”. Recomenda-se executar normalmente na sessão local.
- Domínio vem de `PartOfDomain`; grupo de trabalho recebe indicação explícita de não aplicabilidade.
- Registro aberto somente com leitura, visões 32/64 bits. Office Click-to-Run utiliza `Inventory\Office\16.0`, `OfficeProductReleaseIds` e `OfficePackageVersion`. Não infere ano pelo número 16.0 nem usa `VersionToReport` como estado da instalação.
- MSI/instalações antigas: nomes explícitos em Uninstall, sem executar `Win32_Product` (que pode disparar reparos). Inventário pode conter entradas residuais. IDs desconhecidos são mostrados sem adivinhar o ano. Office 2016 sem indicação explícita de ano pode permanecer sem edição identificada.
- Ativação: consulta `SoftwareLicensingProduct` filtrada pelo ApplicationID do Office, devolvendo somente nome, descrição e status. Não devolve chave de produto. Licenças KMS, MAK e varejo são classificadas apenas quando explicitadas na descrição. Resultados são associados individualmente ao produto, inclusive Visio/Project. Uma licença desses produtos não comprova a ativação da suíte.
- Microsoft 365 moderno: CIM/SPP não cobre integralmente a ativação por assinatura. Esta versão NÃO executa `vnextdiag.ps1`, nem acessa arquivos de licença. Nesses casos retorna “Não identificado”. Uma futura integração somente de listagem precisará de testes com instalações reais e projeção restrita de campos; nunca executar ações remove/reset nem alterar política PowerShell.
- E-mail: somente valor `EmailAddress` nas identidades Office do usuário atual. Pode ser identidade em cache, inclusive múltiplas; não verifica sessão autenticada. Ausência de evidência deixa “Não identificado”. Não lê tokens, cookies, Credential Manager, documentos ou arquivos de perfil.
- Consultas PowerShell têm limite de 35 segundos cada; falhas de acesso e tempo limite não invalidam os campos já coletados. A interface não permite fechar durante consulta para evitar tarefa órfã; tempo esperado máximo de subprocessos é cerca de 70 segundos, além da leitura local.

## Transporte autenticado futuro — não habilitado

A implementação atual não faz rede, não envia e-mail e não inclui bibliotecas de autenticação. `Transport.send(Report)` é o contrato para um adaptador futuro; `DeliveryError` representa falhas. Alterar `config.json` não habilita envio real.

Após definição do provedor, opção sem hospedagem própria: serviço gerenciado da organização com OAuth e identidade corporativa, por exemplo Microsoft 365/Power Automate com entrada autenticada por Entra ID, ou API de e-mail compatível com OAuth delegado. A viabilidade depende do tenant, licenças e permissões; nenhum plano gratuito é presumido. Aplicativo público de desktop não pode guardar segredo de cliente ou senha SMTP. URL de webhook com segredo embutido também não atende ao requisito.

O adaptador deverá obter autenticação no momento do envio por fluxo aprovado (SSO/WAM ou login corporativo, sem exigir configuração de caixa postal pelo colaborador), validar destinatário no serviço, usar HTTPS com validação de certificado, timeout, limites de tamanho, autorização por tenant/grupo e confirmação baseada no aceite do serviço. Não persistir tokens dentro do executável/configuração. Se houver necessidade de cache externo seguro, isso requer definição e autorização prévias.

Tratar indisponibilidade, falhas TLS, 401/403, 429 e timeout com mensagem na interface e preservar relatório para CSV. Não usar repetição automática cega: timeout após aceite pode causar duplicidade; exigir idempotência por requisição. Não fazer fila oculta nem enviar ao reabrir. Testes de rede serão adicionados junto ao adaptador real. Neste modo não há falhas de rede de envio porque nenhuma conexão existe.

## Referências oficiais consultadas

- [Inventário Office Click-to-Run](https://learn.microsoft.com/en-us/microsoft-365-apps/updates/microsoft-guidance-on-office-build-install)
- [Limites do SPP e diagnóstico de ativação Microsoft 365](https://learn.microsoft.com/en-us/microsoft-365-apps/licensing-activation/vnextdiag)
- [PyInstaller e builds por plataforma](https://pyinstaller.org/en/stable/operating-mode.html)

As dependências têm limites de versão no pyproject. Para uma versão corporativa aprovada, registrar e fixar as versões exatas resolvidas no ambiente Windows, arquivar `pip freeze`, hash do artefato e evidência de homologação. Nenhuma estabilidade de build reproduzível é alegada nesta versão inicial.
