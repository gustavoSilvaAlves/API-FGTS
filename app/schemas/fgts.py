import re
from pydantic import BaseModel, Field, field_validator

class CNPJRequest(BaseModel):
    cnpj: str = Field(..., description="CNPJ da empresa com 14 dígitos, sem formatação.")

    @field_validator('cnpj')
    def validate_cnpj(cls, v):
        if not re.fullmatch(r'\d{14}', v):
            raise ValueError('CNPJ deve conter 14 dígitos numéricos.')
        return v

class StatusResponse(BaseModel):
    message: str

class FGTSResponse(BaseModel):
    razao_social: str | None = None
    cnpj: str | None = None
    resultado: str