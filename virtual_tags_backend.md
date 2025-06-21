# 🏷️ Implementação de Virtual Tags - X Cost

## 📋 RESUMO EXECUTIVO

Implementar funcionalidade **Virtual Tags** no X Cost baseada na solução da FinOut. Virtual Tags são regras dinâmicas de alocação de custos que funcionam como uma camada de abstração sobre dados de billing, permitindo 100% de alocação de custos sem modificar infraestrutura existente.

---

## 🔧 PROMPT PARA BACKEND (COPILOT)

### CONTEXTO
Você precisa implementar a API completa de Virtual Tags no backend FastAPI do X Cost. Esta funcionalidade deve processar regras de alocação de custos e aplicá-las aos dados de billing existentes.

### REQUISITOS TÉCNICOS

#### 1. **Modelos de Dados**
```python
# Adicionar ao models.py ou criar virtual_tags_models.py
class VirtualTag(Base):
    __tablename__ = "virtual_tags"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    category = Column(Enum(VirtualTagCategory), nullable=False)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, nullable=False)
    default_value = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID, ForeignKey("users.id"))
    
    rules = relationship("VirtualTagRule", back_populates="virtual_tag", cascade="all, delete-orphan")

class VirtualTagRule(Base):
    __tablename__ = "virtual_tag_rules"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    virtual_tag_id = Column(UUID, ForeignKey("virtual_tags.id"), nullable=False)
    conditions = Column(JSON)  # Array de condições
    action = Column(JSON)      # Ação a executar
    priority = Column(Integer, nullable=False)
    logical_operator = Column(Enum(LogicalOperator), default=LogicalOperator.AND)
    
    virtual_tag = relationship("VirtualTag", back_populates="rules")

class VirtualTagAllocation(Base):
    __tablename__ = "virtual_tag_allocations"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    cost_record_id = Column(UUID, ForeignKey("cost_records.id"))
    virtual_tag_id = Column(UUID, ForeignKey("virtual_tags.id"))
    tag_value = Column(String(255))
    allocated_cost = Column(Numeric(10, 2))
    allocation_date = Column(DateTime, default=datetime.utcnow)
```

#### 2. **API Endpoints**
```python
# Criar virtual_tags_api.py
from fastapi import APIRouter, Depends, HTTPException, Query
from app.auth_security import get_current_user

router = APIRouter(prefix="/api/v1/virtual-tags", tags=["virtual-tags"])

@router.get("/")
async def list_virtual_tags(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    user = Depends(get_current_user)
):
    """Listar Virtual Tags com filtros"""

@router.post("/")
async def create_virtual_tag(
    virtual_tag: VirtualTagCreate,
    user = Depends(get_current_user)
):
    """Criar nova Virtual Tag"""

@router.get("/{tag_id}")
async def get_virtual_tag(
    tag_id: UUID,
    user = Depends(get_current_user)
):
    """Obter Virtual Tag específica"""

@router.put("/{tag_id}")
async def update_virtual_tag(
    tag_id: UUID,
    virtual_tag: VirtualTagUpdate,
    user = Depends(get_current_user)
):
    """Atualizar Virtual Tag"""

@router.delete("/{tag_id}")
async def delete_virtual_tag(
    tag_id: UUID,
    user = Depends(get_current_user)
):
    """Excluir Virtual Tag"""

@router.post("/{tag_id}/preview")
async def preview_allocation(
    tag_id: UUID,
    date_range: DateRangeFilter,
    user = Depends(get_current_user)
):
    """Preview de alocação de custos"""

@router.get("/fields/available")
async def get_available_fields(user = Depends(get_current_user)):
    """Obter campos disponíveis para regras"""

@router.get("/metrics/dashboard")
async def get_dashboard_metrics(
    date_range: Optional[DateRangeFilter] = None,
    user = Depends(get_current_user)
):
    """Métricas para dashboard"""

@router.post("/process-allocation")
async def process_allocation(
    date_range: DateRangeFilter,
    tag_ids: Optional[List[UUID]] = None,
    user = Depends(get_current_user)
):
    """Processar alocação para período"""
```

#### 3. **Engine de Processamento**
```python
# Criar virtual_tags_engine.py
class VirtualTagEngine:
    """Engine para processar regras de Virtual Tags"""
    
    async def process_allocation(
        self,
        date_range: DateRange,
        virtual_tags: List[VirtualTag] = None
    ) -> AllocationResult:
        """Processar alocação de custos baseada em regras"""
        
    async def evaluate_rules(
        self,
        cost_record: CostRecord,
        virtual_tag: VirtualTag
    ) -> Optional[str]:
        """Avaliar regras para um registro de custo"""
        
    async def apply_conditions(
        self,
        cost_record: CostRecord,
        conditions: List[RuleCondition],
        logical_operator: LogicalOperator
    ) -> bool:
        """Aplicar condições de uma regra"""
        
    async def execute_action(
        self,
        cost_record: CostRecord,
        action: RuleAction
    ) -> str:
        """Executar ação de uma regra"""
        
    async def get_allocation_preview(
        self,
        virtual_tag: VirtualTag,
        date_range: DateRange,
        limit: int = 100
    ) -> List[AllocationPreview]:
        """Gerar preview de alocação"""
```

#### 4. **Schemas Pydantic**
```python
# Criar virtual_tags_schemas.py
class VirtualTagBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: VirtualTagCategory
    is_active: bool = True
    priority: int
    default_value: Optional[str] = None

class VirtualTagCreate(VirtualTagBase):
    rules: List[VirtualTagRuleCreate]

class VirtualTagUpdate(VirtualTagBase):
    rules: Optional[List[VirtualTagRuleUpdate]] = None

class VirtualTagResponse(VirtualTagBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    rules: List[VirtualTagRuleResponse]
    
    class Config:
        from_attributes = True
```

#### 5. **Integração com Dados Existentes**
- Conectar com tabela `cost_records` existente
- Usar dados de provedores cloud já coletados
- Aplicar Virtual Tags retroativamente nos dados históricos
- Manter compatibilidade com sistema de autenticação atual

#### 6. **Background Jobs**
```python
# Adicionar ao cost_analytics.py ou criar virtual_tags_jobs.py
from celery import Celery

@celery_app.task
def process_virtual_tags_allocation(date_range: dict, tag_ids: list = None):
    """Job para processar alocação em background"""
    
@celery_app.task
def daily_virtual_tags_processing():
    """Job diário para processar novos dados"""
```

#### 7. **Métricas e Analytics**
```python
class VirtualTagAnalytics:
    async def get_coverage_metrics(self, date_range: DateRange) -> CoverageMetrics:
        """Métricas de cobertura de alocação"""
        
    async def get_allocation_breakdown(self, date_range: DateRange) -> List[AllocationBreakdown]:
        """Breakdown de alocação por categoria"""
        
    async def get_unallocated_costs(self, date_range: DateRange) -> List[UnallocatedCost]:
        """Custos não alocados"""
        
    async def detect_rule_conflicts(self) -> List[RuleConflict]:
        """Detectar conflitos entre regras"""
```

### DELIVERABLES
1. Modelos SQLAlchemy completos
2. Endpoints API com autenticação/autorização
3. Engine de processamento de regras
4. Schemas Pydantic para validação
5. Background jobs para processamento
6. Testes unitários e de integração
7. Migration do banco de dados
8. Documentação em `/shared/docs-backend/virtual-tags.md`

---

## 🔄 INTEGRAÇÃO ENTRE FRONTEND E BACKEND

### Fluxo de Dados
1. **Frontend** cria/edita Virtual Tags via formulário
2. **Backend** valida regras e armazena no banco
3. **Backend** processa alocação em background
4. **Frontend** exibe resultados e métricas

### Comunicação
- Usar axios client existente configurado
- Manter padrões de error handling atuais
- Implementar WebSocket para updates em tempo real (opcional)

### Validações
- **Frontend**: Validação de formulário em tempo real
- **Backend**: Validação de regras e conflitos
- **Ambos**: Validação de permissões por role

---

## 🎯 CRITÉRIOS DE SUCESSO

1. ✅ Interface intuitiva para usuários não-técnicos
2. ✅ Processamento eficiente de grandes volumes de dados
3. ✅ Alocação 100% dos custos (sem untagged)
4. ✅ Performance: <3s para preview, <30s para processamento completo
5. ✅ Retroatividade: aplicar regras a dados históricos
6. ✅ Escalabilidade: suportar centenas de regras
7. ✅ Auditoria: rastrear todas as mudanças
8. ✅ Testes: cobertura >90%

---

## 📚 REFERÊNCIAS TÉCNICAS

- **Especificação FOCUS**: Para padronização de dados de custo
- **FinOut Virtual Tags**: Referência funcional (análise anexa)
- **X Cost atual**: Manter compatibilidade e padrões existentes

Implementem esta funcionalidade mantendo a qualidade e padrões atuais do projeto X Cost!