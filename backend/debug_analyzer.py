#!/usr/bin/env python3
"""
Debug seasonality endpoint issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_database
from app.services.seasonality_analyzer import SeasonalityAnalyzer

def debug_seasonality():
    """Debug seasonality analysis directly"""
    
    try:
        db = next(get_database())
        analyzer = SeasonalityAnalyzer(db)
        
        print("🔍 Testing seasonality analyzer directly...")
        
        result = analyzer.analyze_seasonality(
            provider_name=None,
            period="current_month",
            team_id=None
        )
        
        print("✅ Analyzer working!")
        print(f"Type: {type(result)}")
        print(f"Attributes: {dir(result)}")
        print(f"Monthly comparison: {result.monthly_comparison}")
        print(f"Status: {result.status}")
        print(f"Metadata type: {type(result.metadata)}")
        print(f"Data quality: {result.metadata.data_quality}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_seasonality()
