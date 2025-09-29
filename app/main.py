from fastapi import FastAPI
from app.api.v1.endpoints import fgts

app = FastAPI(
    title="API de Consulta FGTS",
    description="API para verificar a regularidade de empregadores no FGTS.",
    version="1.0.0"
)

app.include_router(fgts.router, prefix="/api/v1/fgts", tags=["FGTS"])

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Consulta FGTS. Acesse /docs para a documentação."}