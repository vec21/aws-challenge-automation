# GitHub PR Analyzer 🌟

![GitHub PR Analyzer](screenshots/banner.png)

Uma ferramenta de linha de comando que automatiza a revisão de código em repositórios GitHub, gerando relatórios detalhados em PDF e disponibilizando-os em uma interface web. 🚀

## Funcionalidades 🎯

* **Análise de Pull Requests** 📋: Extrai informações detalhadas sobre PRs (abertos, fechados ou todos)
* **Análise de Código** 🔍: Detecta problemas como TODOs, FIXMEs e arquivos com muitas alterações
* **Filtro por Data** 🗓️: Permite analisar PRs criados nos últimos N dias
* **Suporte para Múltiplos Repositórios** 📦: Analisa vários repositórios em um único relatório
* **Relatórios em PDF** 📄: Gera relatórios detalhados em formato PDF
* **Interface Web** 🌐: Visualize todos os relatórios em uma interface web amigável
* **Notificações por Email** 📧: Receba alertas quando novos relatórios são gerados

## Pré-requisitos ✅

* Python 3.9+ 🐍
* Conta AWS com acesso para criar recursos (S3, Lambda, SNS) ☁️
* Token de acesso pessoal do GitHub 🔑
* Pulumi CLI instalado ⚙️

## Instalação 🛠️

1. Clone o repositório:

   ```bash
   git clone https://github.com/vec21/aws-challenge-automation.git
   cd aws-challenge-automation
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure o token do GitHub:

   ```bash
   export GITHUB_TOKEN=seu_token_github
   # OU
   pulumi config set github_token seu_token_github --secret
   ```

5. Configure a infraestrutura AWS com Pulumi:

   ```bash
   pulumi up
   ```

## Uso 🚀

### **Comandos Básicos** 🖥️

```bash
   # Analisar um repositório 🌟
   python src/cli.py review-code --repo usuario/repositorio

   # Analisar com estado específico (open, closed, all) 🔄
   python src/cli.py review-code --repo usuario/repositorio --state closed

   # Analisar com limite de dias 🗓️
   python src/cli.py review-code --repo usuario/repositorio --days 14

   # Realizar análise de código 🔍
   python src/cli.py review-code --repo usuario/repositorio --analyze

   # Analisar múltiplos repositórios 📦
   python src/cli.py review-code --repo "usuario/repo1,usuario/repo2"

   # Enviar para S3 e gerar interface web ☁️
   python src/cli.py review-code --repo usuario/repositorio --bucket nome-do-bucket

   # Enviar notificação por email 📧
   python src/cli.py review-code --repo usuario/repositorio --notify --email seu.email@exemplo.com

   # Limitar o número de PRs processados 📉
   python src/cli.py review-code --repo usuario/repositorio --limit 10
```

## **Exemplo Completo** 🌈

### 🔍 Analisar um repositório

```bash
python src/cli.py review-code --repo torvalds/linux
```

```
Reviewing repository torvalds/linux  
Connected to repository: torvalds/linux  
Found 469 pull requests with state 'open'  
Processing up to 100 pull requests...  
Processing PR #1229 (1/100)  
Processing PR #1228 (2/100)  
Processing PR #1227 (3/100)  
...
PDF report generated: linux_open.pdf 📄
```

📄 [Ver relatório PDF](screenshots/linux_open.pdf)

### 🟢 Analisar com estado específico (ex: fechados)

```bash
python src/cli.py review-code --repo torvalds/linux --state closed
```

```
Reviewing repository torvalds/linux
Connected to repository: torvalds/linux
Found 656 pull requests with state 'closed'
Processing up to 100 pull requests...
Processing PR #1223 (1/100)
Processing PR #1219 (2/100)
Processing PR #1217 (3/100)
        ...
PDF report generated: linux_closed.pdf 📄
```

📄 [Analisar estado fechado](screenshots/linux_closed.pdf)

### 🗓️ Analisar com limite de dias (últimos 14 dias)

```bash
python src/cli.py review-code --repo microsoft/vscode --days 14
```

```
Reviewing repository microsoft/vscode  
Connected to repository: microsoft/vscode  
Found 545 pull requests with state 'open'  
Processing up to 100 pull requests...  
Processing PR #248625 (1/100)  
Processing PR #248616 (2/100)  
Processing PR #248552 (3/100)  
...  
PDF report generated: vscode_open.pdf 📄
```

📄 [Ver relatório PDF (últimos 14 dias)](screenshots/vscode_open.pdf)

### 🧠 Realizar análise de código

```bash
python src/cli.py review-code --repo tensorflow/tensorflow --analyze
```

```
Reviewing repository tensorflow/tensorflow
Connected to repository: tensorflow/tensorflow
Found 7997 pull requests with state 'open'
Processing up to 100 pull requests...
Processing PR #93105 (1/100)
Processing PR #93104 (2/100)
Processing PR #93103 (3/100)
         ...
Processing PR #92935 (100/100)
Limit of 100 PRs reached. Use --limit to increase.
PDF report generated: tensorflow_open.pdf 📄
```

📄 [Ver a Análise de código](screenshots/tensorflow_open.pdf)

### 📦 Analisar múltiplos repositórios

```bash
python src/cli.py review-code --repo "microsoft/vscode,tensorflow/tensorflow"
```

```
Reviewing repository microsoft/vscode
Connected to repository: microsoft/vscode
Found 545 pull requests with state 'open'
Processing up to 100 pull requests...
Processing PR #248625 (1/100)
Processing PR #248616 (2/100)
          ...
Processing PR #246051 (55/100)
Reviewing repository tensorflow/tensorflow
Connected to repository: tensorflow/tensorflow
Found 7996 pull requests with state 'open'
Processing up to 100 pull requests...
Processing PR #93104 (1/100)
Processing PR #93103 (2/100)
Processing PR #93101 (3/100)
          ...
Processing PR #92935 (99/100)
Processing PR #92934 (100/100)
Limit of 100 PRs reached. Use --limit to increase.
PDF report generated: multi-repos_open.pdf 📄
```

📄 [Ver múltiplos repositórios](screenshots/multi-repos_open.pdf)

### ☁️ Enviar para S3 e gerar interface web

```bash
python src/cli.py review-code --repo vercel/next.js --bucket vec21-aws-challenge
```

```
Reviewing repository vercel/next.js
Connected to repository: vercel/next.js
Found 762 pull requests with state 'open'
Processing up to 100 pull requests...
Processing PR #79040 (1/100)
Processing PR #79039 (2/100)
Processing PR #79038 (3/100)
           ...
Processing PR #78378 (99/100)
Processing PR #78340 (100/100)
Limit of 100 PRs reached. Use --limit to increase.
PDF report generated: next.js_open.pdf 📄
Report uploaded to S3: https://vec21-aws-challenge.s3.amazonaws.com/reports/2025-05-11/next.js_open_20250511_013336.pdf
```

📄 [Ver relatório PDF](https://vec21-aws-challenge.s3.amazonaws.com/reports/2025-05-11/next.js_open_20250511_013336.pdf)

### 📧 Enviar notificação por email

```bash
python src/cli.py review-code --repo torvalds/linux --notify --email veccpro@gmail.com
```

```
Reviewing repository torvalds/linux
Connected to repository: torvalds/linux
Found 469 pull requests with state 'open'
Processing up to 100 pull requests...
Processing PR #1229 (1/100)
Processing PR #1228 (2/100)
       ...
Processing PR #1203 (16/100)
Processing PR #1201 (17/100)
Processing PR #1199 (18/100)
PDF report generated: linux_open.pdf 📄
Notification sent to: veccpro@gmail.com 📧
```

![Notificação por email](screenshots/email_notification.png)

### 📉 Limitar o número de PRs processados (ex: 10 PRs)

```bash
python src/cli.py review-code --repo vercel/next.js --limit 10
```

```
Reviewing repository vercel/next.js
Connected to repository: vercel/next.js
Found 762 pull requests with state 'open'
Processing up to 10 pull requests...
Processing PR #79040 (1/10)
Processing PR #79039 (2/10)
Processing PR #79038 (3/10)
Processing PR #79037 (4/10)
Processing PR #79036 (5/10)
Processing PR #79035 (6/10)
        ...
Processing PR #79022 (7/10)
Processing PR #79020 (8/10)
Processing PR #79021 (9/10)
Processing PR #79018 (10/10)
Limit of 10 PRs reached. Use --limit to increase.
PDF report generated: next.js_open.pdf 📄
```

📄 [Ver relatório](screenshots/next.js_open.pdf)

## Interface Web 🌐

Após gerar relatórios e enviá-los para o S3, você pode acessar a interface web para visualizar todos os relatórios disponíveis:

**URL de Acesso:**
[Visualizar Relatórios](http://vec21-aws-challenge.s3-website-us-east-1.amazonaws.com)

A interface web permite:

* Visualizar todos os relatórios gerados 📋
* Buscar relatórios por nome, repositório ou estado 🔍
* Baixar os relatórios em PDF 📥
* Ver detalhes como data de criação, tamanho e conteúdo ℹ️

Para atualizar manualmente a interface web:

```bash
export BUCKET_NAME=vec21-aws-challenge
python src/web_interface.py
```

![Interface Web](screenshots/web_interface.png)

## Arquitetura 🏗️

```bash

                                                  +-------------------+
                                                  |                   |
                                                  |  GitHub           |
                                                  |  Repositories     |
                                                  |                   |
                                                  +--------+----------+
                                                           | API Calls
                                                           v
+---------------+     Commands     +---------------+     +--+------------+
|               |                  |               |     |               |
|  Developer    +----------------->+  CLI Tool     +---->+  GitHub API   |
|               |                  |               |     |               |
+---------------+                  +-------+-------+     +---------------+
                                           |
                                           v
                          +----------------+------------------+
                          |                                   |
                          |  PDF Report Generation            |
                          |                                   |
                          +----------------+------------------+
                                           |
                                           v
+---------------+                 +--------+--------+                 +---------------+
|               |                 |                 |                 |               |
|  CloudWatch   +---------------->+  AWS Lambda     +---------------->+  Amazon📄 S3    |
|  Events       |  Scheduled      |                 |  Store Reports  |  Bucket       |
|               |  Execution      |                 |                 |               |
+---------------+                 +--------+--------+                 +-------+-------+
                                           |                                  |
                                           v                                  |
                                  +--------+--------+                         |
                                  |                 |                         |
                                  |  Amazon SNS     |                         |
                                  |  Topic          |                         |
                                  |                 |                         |
                                  +--------+--------+                         |
                                           |                                  |
                                           v                                  v
                                  +--------+--------+                +--------+--------+
                                  |                 |                |                 |
                                  |  Email          |                |  Web Interface  |
                                  |  Notification   |                |  (S3 Website)   |
                                  |                 |                |                 |
                                  +-----------------+                +-----------------+
```

*Gerado por **Amazon Q** 🤖*

O projeto utiliza os seguintes serviços AWS:

* **S3** ☁️: Armazenamento de relatórios PDF e hospedagem da interface web
* **Lambda** ⚡: Execução programada da análise de código
* **SNS** 📬: Envio de notificações por email
* **CloudWatch Events** ⏰: Agendamento de execuções periódicas

## Como o Amazon Q Developer ajudou 🧠

O Amazon Q Developer foi fundamental no desenvolvimento desta ferramenta através de seus comandos especializados:

### `/dev` - Desenvolvimento de Código 💻

* Gerou o esqueleto inicial da CLI com integração GitHub e S3 🛠️
* Implementou a estrutura base do projeto usando Pulumi para infraestrutura AWS 🏗️
* Criou a função Lambda para execução programada da análise ⚡
* Desenvolveu a integração com SNS para notificações por email 📧

### `/review` - Revisão e Otimização 🔍

* Otimizou o código em `src/cli.py` adicionando mecanismos de retry para lidar com limites de taxa da API ⚙️
* Melhorou a geração de relatórios PDF com tabelas e formatação avançada 📄
* Sugeriu correções para problemas de comparação de datas com diferentes fusos horários 🌐
* Identificou e corrigiu potenciais problemas de segurança 🔒

### `/test` - Geração de Testes 🧪

* Criou testes unitários para as principais funções do projeto ✅
* Implementou testes de integração para verificar o fluxo completo 🔄
* Gerou fixtures e mocks para simular interações com serviços externos 🎭
* Configurou a estrutura de testes com pytest 🛠️

### `/doc` - Documentação 📝

* Gerou documentação detalhada para as funções e classes 📚
* Criou o diagrama de arquitetura para visualizar o fluxo de dados 📊
* Produziu exemplos de uso para cada funcionalidade 📖
* Desenvolveu o README completo com instruções de instalação e uso 📜

O Amazon Q ajudou a implementar as 5 funcionalidades principais:

1. **Análise de código** 🔍: Detectando problemas como TODOs, FIXMEs e arquivos com muitas alterações
2. **Filtro por data** 🗓️: Permitindo analisar PRs criados nos últimos N dias
3. **Notificações por email** 📧: Enviando alertas quando novos relatórios são gerados
4. **Suporte para múltiplos repositórios** 📦: Analisando vários repositórios em um único relatório
5. **Interface web** 🌐: Disponibilizando uma interface amigável para visualizar os relatórios

## Testes 🧪

### O projeto inclui testes unitários e de integração:

```bash
# Instalar dependências de teste
pip install -r requirements-test.txt

# Executar todos os testes
pytest

# Executar testes com cobertura
pytest --cov=src
```

## Licença 📜

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
