#!/usr/bin/env python3
import asyncio
import os
import sys
sys.path.append('.')

# Carregar variáveis de ambiente do .env
from dotenv import load_dotenv
load_dotenv()

from localstack_aws_service import create_localstack_aws_service

async def test():
    print(f"AWS_ENDPOINT_URL: {os.getenv('AWS_ENDPOINT_URL')}")
    print(f"Should use LocalStack: {'localhost:4566' in os.getenv('AWS_ENDPOINT_URL', '')}")
    
    service = create_localstack_aws_service()
    print('✅ Serviço LocalStack criado')
    
    savings = await service.get_aws_savings(min_savings=50.0)
    print(f'✅ {len(savings)} oportunidades encontradas')
    
    for opp in savings:
        print(f'   - {opp.id}: ${opp.estimated_savings:.2f} ({opp.opportunity_type.value})')

if __name__ == "__main__":
    asyncio.run(test())
