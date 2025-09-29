from fastapi import APIRouter, Body, HTTPException, status, Depends
from app.schemas.fgts import CNPJRequest, FGTSResponse, StatusResponse
from app.services.scraper import get_initial_info, solve_captcha, submit_fgts_query, FGTSServiceError
from app.core.config import Settings, settings as default_settings
import httpx

router = APIRouter()


@router.get("/status", response_model=StatusResponse, tags=["FGTS"])
async def get_status():
    """Endpoint de verificação de status da API."""
    return {"message": "sucesso"}


@router.post("/consulta", response_model=FGTSResponse, tags=["FGTS"])
async def consulta_fgts(
        request_data: CNPJRequest = Body(...),
        settings: Settings = Depends(lambda: default_settings)
):
    """Consulta a regularidade de um CNPJ no sistema do FGTS."""
    cnpj = request_data.cnpj
    try:
        async with httpx.AsyncClient(verify=False) as client:
            # Etapa 1: Obter informações iniciais
            initial_info = await get_initial_info(client)

            # Etapa 2: Resolver o captcha
            captcha_text = await solve_captcha(client, initial_info["captcha_base64"], settings.CAPTCHA_API_KEY)

            # Etapa 3: Submeter a consulta
            result = await submit_fgts_query(client, cnpj, initial_info, captcha_text)

            return result

    except FGTSServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erro no serviço de consulta: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro interno inesperado: {e}"
        )