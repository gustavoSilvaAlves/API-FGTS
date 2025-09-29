# API de Consulta de Regularidade do FGTS

![Status](https://img.shields.io/badge/status-ativo-success)
![Versão](https://img.shields.io/badge/versão-1.0.0-blue)
![Licença](https://img.shields.io/badge/licença-MIT-green)

Uma API RESTful robusta e assíncrona, construída com FastAPI e containerizada com Docker, para consultar a situação de regularidade de um CNPJ no sistema do FGTS da Caixa Econômica Federal.

---

## ✨ Funcionalidades

- **Consulta por CNPJ**: Endpoint para verificar se uma empresa está regular ou irregular no FGTS.
- **Alta Performance**: Construída com FastAPI, a API é totalmente assíncrona, capaz de lidar com múltiplas requisições simultâneas.
- **Web Scraping Inteligente**: Extrai informações diretamente do site da Caixa, utilizando `httpx` e `BeautifulSoup`.
- **Resolução de Captcha**: Integra-se com o serviço 2Captcha para resolver os captchas necessários para a consulta.
- **Containerização**: Totalmente configurada com Docker e Docker Compose para um ambiente de desenvolvimento e produção padronizado e portátil.
- **Documentação Automática**: Interface interativa do Swagger UI (`/docs`) e ReDoc (`/redoc`) gerada automaticamente pelo FastAPI.

---

## 🛠️ Tecnologias Utilizadas

- **Backend**: FastAPI, Pydantic, Uvicorn
- **HTTP Client**: HTTPL
- **Web Scraping**: BeautifulSoup4
- **Containerização**: Docker, Docker Compose
- **Linguagem**: Python 3.11

---

## 🚀 Como Executar o Projeto

### Pré-requisitos

Antes de começar, você vai precisar ter instalado em sua máquina:
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/](https://github.com/)<SEU_USUARIO>/<NOME_DO_REPOSITORIO>.git
    cd <NOME_DO_REPOSITORIO>
    ```

2.  **Configure as variáveis de ambiente:**
    - Renomeie o arquivo `.env.example` para `.env`.
    - Abra o arquivo `.env` e insira sua chave da API do 2Captcha:
      ```dotenv
      CAPTCHA_API_KEY="SUA_CHAVE_API_AQUI"
      ```

3.  **Inicie a aplicação com Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    A API estará disponível em `http://localhost:8302`.

---

## Como Usar a API

Após iniciar a aplicação, você pode acessar a documentação interativa em:

- **Swagger UI**: `http://localhost:8302/docs`
- **ReDoc**: `http://localhost:8302/redoc`

### Exemplo de Requisição (usando `curl`)

```bash
curl -X 'POST' \
  'http://localhost:8302/api/v1/fgts/consulta' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "cnpj": "08007812000170"
}'
```

### Exemplo de Resposta (Regular)
```json
{
  "razao_social": "NEYMAR SPORT E MARKETING LIMITADA",
  "cnpj": "08.007.812/0001-70",
  "resultado": "A empresa informada está REGULAR perante o FGTS."
}
```

### Exemplo de Resposta (Irregular)
```json
{
  "razao_social": "OI S.A. - EM RECUPERACAO JUDICIAL",
  "cnpj": "76.535.764/0001-43",
  "resultado": "A empresa informada está IRREGULAR perante o FGTS."
}
```

---

## 📝 Licença


Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
