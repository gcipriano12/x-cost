"""
Database migration for Virtual Tags
Criar tabelas para sistema de Virtual Tags
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'virtual_tags_001'
down_revision = None  # Substituir pelo último revision ID
branch_labels = None
depends_on = None

def upgrade():
    """Criar tabelas para Virtual Tags"""
    
    # Tabela virtual_tags
    op.create_table(
        'virtual_tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text()),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('priority', sa.Integer(), nullable=False, default=100),
        sa.Column('default_value', sa.String(255)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        schema='finops'
    )
    
    # Índices para virtual_tags
    op.create_index('idx_virtual_tags_name', 'virtual_tags', ['name'], schema='finops')
    op.create_index('idx_virtual_tags_category', 'virtual_tags', ['category'], schema='finops')
    op.create_index('idx_virtual_tags_is_active', 'virtual_tags', ['is_active'], schema='finops')
    op.create_index('idx_virtual_tags_priority', 'virtual_tags', ['priority'], schema='finops')
    
    # Tabela virtual_tag_rules
    op.create_table(
        'virtual_tag_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('virtual_tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('conditions', postgresql.JSONB()),
        sa.Column('action', postgresql.JSONB()),
        sa.Column('priority', sa.Integer(), nullable=False, default=100),
        sa.Column('logical_operator', sa.String(10), default='AND'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='finops'
    )
    
    # Foreign key para virtual_tag_rules
    op.create_foreign_key(
        'fk_virtual_tag_rules_virtual_tag_id',
        'virtual_tag_rules', 'virtual_tags',
        ['virtual_tag_id'], ['id'],
        source_schema='finops', referent_schema='finops',
        ondelete='CASCADE'
    )
    
    # Índices para virtual_tag_rules
    op.create_index('idx_virtual_tag_rules_virtual_tag_id', 'virtual_tag_rules', ['virtual_tag_id'], schema='finops')
    op.create_index('idx_virtual_tag_rules_priority', 'virtual_tag_rules', ['priority'], schema='finops')
    op.create_index('idx_virtual_tag_rules_is_active', 'virtual_tag_rules', ['is_active'], schema='finops')
    
    # Tabela virtual_tag_allocations
    op.create_table(
        'virtual_tag_allocations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('cost_record_id', sa.Integer(), nullable=False),
        sa.Column('virtual_tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_value', sa.String(255), nullable=False),
        sa.Column('allocated_cost', sa.Numeric(15, 4), nullable=False),
        sa.Column('allocation_percentage', sa.Numeric(5, 2), default=100.0),
        sa.Column('allocation_date', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('processed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='finops'
    )
    
    # Foreign keys para virtual_tag_allocations
    op.create_foreign_key(
        'fk_virtual_tag_allocations_cost_record_id',
        'virtual_tag_allocations', 'focus_cost_data',
        ['cost_record_id'], ['id'],
        source_schema='finops', referent_schema='finops',
        ondelete='CASCADE'
    )
    
    op.create_foreign_key(
        'fk_virtual_tag_allocations_virtual_tag_id',
        'virtual_tag_allocations', 'virtual_tags',
        ['virtual_tag_id'], ['id'],
        source_schema='finops', referent_schema='finops',
        ondelete='CASCADE'
    )
    
    # Índices para virtual_tag_allocations
    op.create_index('idx_virtual_tag_allocations_cost_record_id', 'virtual_tag_allocations', ['cost_record_id'], schema='finops')
    op.create_index('idx_virtual_tag_allocations_virtual_tag_id', 'virtual_tag_allocations', ['virtual_tag_id'], schema='finops')
    op.create_index('idx_virtual_tag_allocations_tag_value', 'virtual_tag_allocations', ['tag_value'], schema='finops')
    op.create_index('idx_virtual_tag_allocations_allocation_date', 'virtual_tag_allocations', ['allocation_date'], schema='finops')
    
    # Tabela virtual_tag_processing_logs
    op.create_table(
        'virtual_tag_processing_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('processing_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('virtual_tag_id', postgresql.UUID(as_uuid=True)),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='processing'),
        sa.Column('records_processed', sa.Integer(), default=0),
        sa.Column('records_allocated', sa.Integer(), default=0),
        sa.Column('total_cost_allocated', sa.Numeric(15, 4), default=0),
        sa.Column('error_message', sa.Text()),
        sa.Column('processing_time_seconds', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        schema='finops'
    )
    
    # Foreign key para virtual_tag_processing_logs
    op.create_foreign_key(
        'fk_virtual_tag_processing_logs_virtual_tag_id',
        'virtual_tag_processing_logs', 'virtual_tags',
        ['virtual_tag_id'], ['id'],
        source_schema='finops', referent_schema='finops',
        ondelete='SET NULL'
    )
    
    # Índices para virtual_tag_processing_logs
    op.create_index('idx_virtual_tag_processing_logs_processing_id', 'virtual_tag_processing_logs', ['processing_id'], schema='finops')
    op.create_index('idx_virtual_tag_processing_logs_status', 'virtual_tag_processing_logs', ['status'], schema='finops')
    op.create_index('idx_virtual_tag_processing_logs_created_at', 'virtual_tag_processing_logs', ['created_at'], schema='finops')

def downgrade():
    """Remover tabelas de Virtual Tags"""
    
    # Remover tabelas na ordem correta (devido a foreign keys)
    op.drop_table('virtual_tag_processing_logs', schema='finops')
    op.drop_table('virtual_tag_allocations', schema='finops')
    op.drop_table('virtual_tag_rules', schema='finops')
    op.drop_table('virtual_tags', schema='finops')
    
    # Remover enum types
    op.execute('DROP TYPE IF EXISTS logical_operator')
    op.execute('DROP TYPE IF EXISTS virtualtag_category')
