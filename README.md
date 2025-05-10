# AWS Challenge: Automação
CLI para revisão de código com Amazon Q Developer (#awschallenge).

## Progresso
- [x] Configurado Pulumi para S3, Lambda, e política pública.
- [x] Criado CLI com integração GitHub API e S3.
- [x] Resolvido erro de BlockPublicPolicy.
- [x] Configurado GITHUB_TOKEN como variável de ambiente.
- [x] Validado CLI com subcomando 'review-code' e geração de PDF.
- [ ] Integrar /review programaticamente.
- [ ] Adicionar notificações SNS.
- [ ] Gerar testes com /test.

## Uso do Amazon Q
- Usei `/dev` para gerar o CLI com integração GitHub e S3.
- Usei `/review` para otimizar cli.py, adicionando tabelas no PDF.

## Segurança
- O token GitHub é configurado como variável de ambiente (GITHUB_TOKEN) no Lambda (AWS Console) e localmente.

##
##



# GitHub PR Analyzer

![GitHub PR Analyzer](screenshots/banner.png)

Uma ferramenta de linha de comando que automatiza a revisão de código em repositórios GitHub, gerando relatórios detalhados em PDF e disponibilizando-os em uma interface web.

## Funcionalidades

- **Análise de Pull Requests**: Extrai informações detalhadas sobre PRs (abertos, fechados ou todos)
- **Análise de Código**: Detecta problemas como TODOs, FIXMEs e arquivos com muitas alterações
- **Filtro por Data**: Permite analisar PRs criados nos últimos N dias
- **Suporte para Múltiplos Repositórios**: Analisa vários repositórios em um único relatório
- **Relatórios em PDF**: Gera relatórios detalhados em formato PDF
- **Interface Web**: Visualize todos os relatórios em uma interface web amigável
- **Notificações por Email**: Receba alertas quando novos relatórios são gerados

## Pré-requisitos

- Python 3.9+
- Conta AWS com acesso para criar recursos (S3, Lambda, SNS)
- Token de acesso pessoal do GitHub
- Pulumi CLI instalado

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/vec21/aws-challenge-automation.git
   cd aws-challenge-automation

