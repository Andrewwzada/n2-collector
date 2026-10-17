# Roteiro de homologação Windows

Este roteiro requer execução manual em máquinas de teste autorizadas. Ainda não foi executado neste ambiente Linux.

1. Windows 10 e 11, conta comum: confirmar que a abertura não coleta dados, não pede elevação e mostra aviso/modo de testes.
2. Clicar uma vez; verificar progresso, interface responsiva, bloqueio de clique duplicado, resultado e confirmação explícita de simulação. Verificar que fechar não abandona uma consulta em execução.
3. Comparar hostname, usuário, domínio/grupo de trabalho e edição/build Windows com as propriedades do sistema, incluindo sessão RDP se utilizada na ACIJ.
4. Testar Office ausente, Office MSI 2016, 2019, LTSC 2021, LTSC 2024 e Microsoft 365, em 32/64 bits. Comparar edição com Arquivo > Conta; confirmar que valores não comprovados ficam “Não identificado”. Incluir coexistência de Visio/Project.
5. Comparar licenças KMS/MAK/varejo, estados não ativados, permissões negadas e falha/timeout CIM. Não atribuir a ativação de Visio ao Office. Confirmar limitações documentadas do Microsoft 365.
6. Testar identidade Office ausente, uma conta e várias contas. Confirmar aviso de cache; não validar a conta como sessão ativa.
7. Confirmar botão único “Enviar para Andrew”, ausência de exportação e relatório com rolagem sem aumentar a janela.
8. Testar configuração ausente, JSON inválido e mode diferente de test: nenhum envio pode ocorrer. Monitorar rede em ambiente de teste e confirmar ausência de tráfego originado pelo aplicativo.
9. Gerar `.exe` no Windows, testar em máquina limpa sem Python, inclusive execução UNC. Validar assinatura, hash e avaliação por Defender/SmartScreen/políticas corporativas, sem desabilitar proteções.
10. Revisar avisos, legibilidade com escala 100%/125%/150%/200%, logo transparente e janela centralizada, navegação por teclado e resolução utilizada pelos colaboradores. Registrar versões de Python, PySide6 e PyInstaller, resultados e pendências antes de liberar.
