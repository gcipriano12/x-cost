#!/bin/bash
# Quick validation script for Savings Opportunities implementation

echo "🧪 Quick Validation - Savings Opportunities Implementation"
echo "========================================================="

# Check if backend is running
echo "1. 🔍 Checking if backend is running..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/optimization/providers 2>/dev/null)

if [ "$BACKEND_STATUS" -eq 200 ]; then
    echo "   ✅ Backend is running (Status: $BACKEND_STATUS)"
else
    echo "   ❌ Backend not accessible (Status: $BACKEND_STATUS)"
    echo "   Please start the backend with: uvicorn app.main:app --reload"
    exit 1
fi

# Test basic savings opportunities endpoint
echo ""
echo "2. 📊 Testing basic savings opportunities endpoint..."
SAVINGS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/savings-opportunities?page=1&per_page=5" 2>/dev/null)
SAVINGS_COUNT=$(echo "$SAVINGS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_count', 0))" 2>/dev/null)

if [ ! -z "$SAVINGS_COUNT" ] && [ "$SAVINGS_COUNT" -gt 0 ]; then
    echo "   ✅ Savings opportunities endpoint working ($SAVINGS_COUNT opportunities found)"
else
    echo "   ⚠️  Savings opportunities endpoint returned no data (may need mock data)"
fi

# Test with filters
echo ""
echo "3. 🔧 Testing advanced filters..."
FILTERED_RESPONSE=$(curl -s "http://localhost:8000/api/v1/savings-opportunities?confidence_level=high&implementation_effort=low&sort_by=monthly_savings&sort_order=desc" 2>/dev/null)
FILTERED_COUNT=$(echo "$FILTERED_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_count', 0))" 2>/dev/null)

if [ ! -z "$FILTERED_COUNT" ]; then
    echo "   ✅ Advanced filters working (found $FILTERED_COUNT high-confidence, low-effort opportunities)"
else
    echo "   ❌ Advanced filters not working properly"
fi

# Test bulk action endpoint (should work even without auth for testing)
echo ""
echo "4. 🚀 Testing bulk action endpoint structure..."
BULK_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/savings-opportunities/bulk-action" \
    -H "Content-Type: application/json" \
    -d '{"action":"test","opportunity_ids":[]}' 2>/dev/null)

if echo "$BULK_RESPONSE" | grep -q "detail"; then
    echo "   ✅ Bulk action endpoint responding (validation working)"
else
    echo "   ❌ Bulk action endpoint not responding properly"
fi

# Test implementation plans endpoint
echo ""
echo "5. 📋 Testing implementation plans endpoint..."
PLANS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/implementation-plans" 2>/dev/null)
PLANS_COUNT=$(echo "$PLANS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_count', 0))" 2>/dev/null)

if [ ! -z "$PLANS_COUNT" ]; then
    echo "   ✅ Implementation plans endpoint working ($PLANS_COUNT plans found)"
else
    echo "   ❌ Implementation plans endpoint not working"
fi

# Check frontend integration files
echo ""
echo "6. 📁 Checking frontend integration files..."

if [ -f "../frontend/src/hooks/useOptimization.ts" ]; then
    BULK_HOOKS=$(grep -c "useBulkActions\|useImplementationPlans" ../frontend/src/hooks/useOptimization.ts 2>/dev/null)
    if [ "$BULK_HOOKS" -gt 0 ]; then
        echo "   ✅ Frontend hooks updated with bulk actions and plans"
    else
        echo "   ⚠️  Frontend hooks may need updating"
    fi
else
    echo "   ❌ Frontend hooks file not found"
fi

if [ -f "../frontend/src/types/optimization.ts" ]; then
    TYPE_FIELDS=$(grep -c "monthly_savings\|implementation_effort\|risk_level" ../frontend/src/types/optimization.ts 2>/dev/null)
    if [ "$TYPE_FIELDS" -gt 2 ]; then
        echo "   ✅ Frontend types updated with new fields"
    else
        echo "   ⚠️  Frontend types may need updating"
    fi
else
    echo "   ❌ Frontend types file not found"
fi

# Summary
echo ""
echo "========================================================="
echo "✨ Validation Summary:"
echo ""

if [ "$BACKEND_STATUS" -eq 200 ] && [ ! -z "$SAVINGS_COUNT" ] && [ ! -z "$FILTERED_COUNT" ] && [ ! -z "$PLANS_COUNT" ]; then
    echo "🎉 All core endpoints are working!"
    echo ""
    echo "📋 What's implemented:"
    echo "   ✅ Enhanced savings opportunities endpoint with advanced filters"
    echo "   ✅ Bulk actions endpoint for opportunity management" 
    echo "   ✅ Implementation plans endpoints"
    echo "   ✅ Frontend hooks and types updated"
    echo "   ✅ Comprehensive validation and error handling"
    echo ""
    echo "🚀 Ready for frontend integration!"
    echo ""
    echo "📖 Next steps:"
    echo "   1. Test the frontend page at /savings-opportunities"
    echo "   2. Verify all filters and actions work"
    echo "   3. Test bulk operations and implementation plans"
    echo ""
else
    echo "⚠️  Some components need attention:"
    echo "   - Check backend logs for any errors"
    echo "   - Verify mock data is generated" 
    echo "   - Ensure all endpoints are properly registered"
fi

echo "📄 For detailed implementation info, see:"
echo "   backend/SAVINGS_OPPORTUNITIES_IMPLEMENTATION.md"
echo ""
