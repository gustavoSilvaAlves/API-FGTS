# Etapa 1: Escolher a imagem base oficial do Python.
# A tag "slim" é uma versão mais leve, ideal para produção.
FROM python:3.11-slim

# Etapa 2: Definir o diretório de trabalho dentro do container.
# Todos os comandos a seguir serão executados a partir deste diretório.
WORKDIR /app

# Etapa 3: Otimização de cache do Docker.
# Copiamos primeiro o arquivo de dependências e as instalamos.
# O Docker só re-executará esta etapa se o requirements.txt mudar.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 4: Copiar o restante do código da aplicação para o diretório de trabalho.
COPY ./app /app/app

# Etapa 5: Expor a porta que a aplicação vai usar dentro do container.
# O Uvicorn, por padrão, roda na porta 8000.
EXPOSE 8000

# Etapa 6: Definir o comando para iniciar a aplicação.
# Usamos uvicorn diretamente. O host 0.0.0.0 é essencial para que a aplicação
# seja acessível de fora do container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]