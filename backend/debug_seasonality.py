#!/usr/bin/env python3
"""
Debug seasonality analysis with real data insights
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_database
from app.services.seasonality_analyzer import SeasonalityAnalyzer
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models import FocusCostData

def debug_seasonality_analysis():
    """Debug how real data is being processed"""
    
    db = next(get_database())
    analyzer = SeasonalityAnalyzer(db)
    
    print("🔍 Debug: Seasonality Analysis with Real Data")
    print("=" * 60)
    
    # Get raw historical data
    print("📊 Getting historical data...")
    historical_data = analyzer._get_historical_data()
    
    print(f"📈 Historical data points: {len(historical_data)}")
    
    if len(historical_data) > 0:
        # Show sample of real data
        print("\n💰 Sample of REAL data being processed:")
        for i, row in enumerate(historical_data[:5]):
            print(f"  {i+1}. Date: {row['date']}, Cost: ${row['cost']:,.2f}, Provider: {row['provider']}")
        
        # Show data distribution by month
        print("\n📅 Real cost distribution by month:")
        monthly_costs = {}
        for row in historical_data:
            month_key = f"{row['year']}-{row['month']:02d}"
            if month_key not in monthly_costs:
                monthly_costs[month_key] = 0
            monthly_costs[month_key] += row['cost']
        
        # Show last 12 months
        for month_key in sorted(monthly_costs.keys())[-12:]:
            cost = monthly_costs[month_key]
            print(f"  {month_key}: ${cost:,.2f}")
        
        # Calculate actual metrics step by step
        print("\n🧮 Real metrics calculations:")
        
        monthly_comp = analyzer._calculate_monthly_comparison(historical_data)
        print(f"  Monthly Comparison (real calc): {monthly_comp:.1f}%")
        
        weekly_pattern = analyzer._calculate_weekly_pattern(historical_data)
        print(f"  Weekly Pattern (real calc): {weekly_pattern:.1f}%")
        
        seasonal_progress = analyzer._calculate_seasonal_progress(historical_data)
        print(f"  Seasonal Progress (real calc): {seasonal_progress:.1f}%")
        
        trend_variation = analyzer._calculate_trend_variation(historical_data)
        print(f"  Trend Variation (real calc): {trend_variation:.1f}%")
        
        # Show current month vs historical comparison details
        current_month = datetime.utcnow().month
        current_year = datetime.utcnow().year
        
        current_month_costs = [
            row['cost'] for row in historical_data 
            if row['month'] == current_month and row['year'] == current_year
        ]
        
        historical_same_month = [
            row['cost'] for row in historical_data 
            if row['month'] == current_month and row['year'] < current_year
        ]
        
        print(f"\n📊 July 2025 vs Historical July analysis:")
        print(f"  Current July 2025 data points: {len(current_month_costs)}")
        print(f"  Historical July data points: {len(historical_same_month)}")
        
        if current_month_costs:
            current_avg = sum(current_month_costs) / len(current_month_costs)
            print(f"  Current July average: ${current_avg:,.2f}")
        
        if historical_same_month:
            historical_avg = sum(historical_same_month) / len(historical_same_month)
            print(f"  Historical July average: ${historical_avg:,.2f}")
            
            if current_month_costs and historical_avg > 0:
                comparison = (current_avg / historical_avg) * 100
                print(f"  Comparison ratio: {comparison:.1f}%")
    
    else:
        print("❌ No historical data found")
    
    db.close()

if __name__ == "__main__":
    debug_seasonality_analysis()
