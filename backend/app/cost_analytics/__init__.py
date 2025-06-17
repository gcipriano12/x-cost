"""
Cost Analytics Module

Módulo modular para análise de custos, orçamentos e dashboards
"""

# Manter compatibilidade com código existente
try:
    from .analytics.cost_analyzer import CostAnalyzer
    from .budget.budget_analyzer import BudgetAnalyzer  
    from .dashboard.dashboard_analyzer import DashboardAnalyzer
    
    __all__ = [
        'CostAnalyzer',
        'BudgetAnalyzer', 
        'DashboardAnalyzer'
    ]
except ImportError:
    # Fallback para estrutura antiga durante transição
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Using legacy cost_analytics structure during refactoring transition")
    
    # Import temporário da estrutura antiga
    import sys
    import os
    import importlib.util
    
    # Adicionar path para importar estrutura antiga se necessário
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    
    try:
        # Tentar importar da estrutura antiga
        old_cost_analytics_path = os.path.join(parent_dir, 'cost_analytics.py')
        if os.path.exists(old_cost_analytics_path):
            spec = importlib.util.spec_from_file_location("old_cost_analytics", old_cost_analytics_path)
            old_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(old_module)
            
            CostAnalyzer = old_module.CostAnalyzer
            BudgetAnalyzer = old_module.BudgetAnalyzer
            DashboardAnalyzer = old_module.DashboardAnalyzer
            
            __all__ = ['CostAnalyzer', 'BudgetAnalyzer', 'DashboardAnalyzer']
        else:
            raise ImportError("Neither new nor old cost_analytics structure found")
            
    except Exception as e:
        logger.error(f"Failed to import cost analytics: {e}")
        # Criar classes placeholder para evitar erros de importação
        class CostAnalyzer:
            def __init__(self, *args, **kwargs):
                raise NotImplementedError("CostAnalyzer refactoring in progress")
        
        class BudgetAnalyzer:
            def __init__(self, *args, **kwargs):
                raise NotImplementedError("BudgetAnalyzer refactoring in progress")
        
        class DashboardAnalyzer:
            def __init__(self, *args, **kwargs):
                raise NotImplementedError("DashboardAnalyzer refactoring in progress")
        
        __all__ = ['CostAnalyzer', 'BudgetAnalyzer', 'DashboardAnalyzer']