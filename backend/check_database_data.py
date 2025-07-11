#!/usr/bin/env python3
"""
Check database data for seasonality analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_database
from app.models import FocusCostData
from sqlalchemy import func
from datetime import datetime, timedelta

def check_database_data():
    """Check what data exists in the database"""
    
    db = next(get_database())
    
    print("🔍 Checking FocusCostData table...")
    
    # Total records
    total_count = db.query(FocusCostData).count()
    print(f"📊 Total records: {total_count:,}")
    
    if total_count == 0:
        print("❌ No data found in database!")
        return
    
    # Date range
    date_range = db.query(
        func.min(FocusCostData.billing_period_start).label('oldest'),
        func.max(FocusCostData.billing_period_start).label('newest')
    ).first()
    
    print(f"📅 Data range: {date_range.oldest} to {date_range.newest}")
    
    # Data by provider
    provider_counts = db.query(
        FocusCostData.provider_name,
        func.count(FocusCostData.id).label('count'),
        func.sum(FocusCostData.billed_cost).label('total_cost')
    ).group_by(FocusCostData.provider_name).all()
    
    print("\n💰 Data by provider:")
    for provider in provider_counts:
        cost = float(provider.total_cost or 0)
        print(f"  {provider.provider_name}: {provider.count:,} records, ${cost:,.2f}")
    
    # Check recent data (last 30 days)
    recent_cutoff = datetime.utcnow().date() - timedelta(days=30)
    recent_count = db.query(FocusCostData).filter(
        FocusCostData.billing_period_start >= recent_cutoff
    ).count()
    
    print(f"\n📈 Recent data (last 30 days): {recent_count:,} records")
    
    # Check if we have enough data for seasonality (180 days = 6 months)
    historical_cutoff = datetime.utcnow().date() - timedelta(days=180)
    historical_count = db.query(FocusCostData).filter(
        FocusCostData.billing_period_start >= historical_cutoff
    ).count()
    
    print(f"🔢 Historical data (last 6 months): {historical_count:,} records")
    
    if historical_count < 180:
        print("⚠️  Not enough data for full seasonality analysis (minimum 180 records)")
        print("🔄 Fallback data will be used")
    else:
        print("✅ Sufficient data for real seasonality analysis")
    
    db.close()

if __name__ == "__main__":
    check_database_data()
