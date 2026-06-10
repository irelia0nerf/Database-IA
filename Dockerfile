# Imagem do KB MCP server para deploy no Cloud Run.
# Build a partir da RAIZ do repo (a base de conhecimento inteira vai na imagem):
#   gcloud run deploy foundlab-kb-mcp --source .
FROM python:3.11-slim

WORKDIR /app

# Dependências primeiro (cache de camada).
COPY tools/kb-mcp/requirements.txt /app/tools/kb-mcp/requirements.txt
RUN pip install --no-cache-dir -r /app/tools/kb-mcp/requirements.txt

# Conteúdo da base + servidor.
COPY . /app

# Cloud Run injeta PORT; o servidor já o honra. KB_AUTH_TOKEN deve ser definido no deploy.
ENV KB_ROOT=/app \
    KB_TRANSPORT=streamable-http \
    KB_HOST=0.0.0.0

EXPOSE 8080
CMD ["python", "tools/kb-mcp/server.py"]
