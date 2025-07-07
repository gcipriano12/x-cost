"""
Modelos Pydantic para Account Distribution endpoint
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class AccountDistributionItem(BaseModel):
    """Item individual da distribuição de contas"""
    account_id: str = Field(..., description="ID único da conta")
    billing_account_name: str = Field(..., description="Nome da conta/billing account")
    percentage: float = Field(..., description="Porcentagem do custo total", ge=0, le=100)
    total_cost: float = Field(..., description="Custo total da conta no período", ge=0)


class AccountDistributionResponse(BaseModel):
    """Resposta completa do endpoint account distribution"""
    success: bool = Field(default=True, description="Status da operação")
    data: List[AccountDistributionItem] = Field(..., description="Lista de distribuição de contas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [
                    {
                        "account_id": "ocid1.tenancy.oc1..prod123456789",
                        "billing_account_name": "Oracle Production Tenancy",
                        "percentage": 64.5,
                        "total_cost": 1095829.48
                    },
                    {
                        "account_id": "ocid1.tenancy.oc1..dev987654321",
                        "billing_account_name": "Oracle Development Tenancy",
                        "percentage": 35.5,
                        "total_cost": 600000.00
                    }
                ]
            }
        }
