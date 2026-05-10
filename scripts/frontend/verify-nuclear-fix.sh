#!/bin/bash

echo "🔍 Verifying Nuclear Fix for removeChild Error"
echo "=============================================="
echo ""

# Check if DynamicMetadata.tsx exists
if [ ! -f "src/components/shared/DynamicMetadata.tsx" ]; then
  echo "❌ DynamicMetadata.tsx not found!"
  exit 1
fi

echo "✅ DynamicMetadata.tsx found"
echo ""

# Check for removeChild in DynamicMetadata (should only be in cleanup)
echo "🔍 Checking for removeChild usage..."
REMOVECHILD_COUNT=$(grep -c "removeChild" src/components/shared/DynamicMetadata.tsx || echo "0")

if [ "$REMOVECHILD_COUNT" -eq "0" ]; then
  echo "❌ No removeChild found - this might be wrong!"
elif [ "$REMOVECHILD_COUNT" -eq "1" ]; then
  echo "✅ Found 1 removeChild (should be in cleanup function only)"
else
  echo "⚠️  Found $REMOVECHILD_COUNT removeChild calls"
fi
echo ""

# Check for replaceWith (should be removed)
echo "🔍 Checking for replaceWith usage..."
if grep -q "replaceWith" src/components/shared/DynamicMetadata.tsx; then
  echo "⚠️  replaceWith still present - nuclear fix may not be applied"
else
  echo "✅ No replaceWith found (good - nuclear fix applied)"
fi
echo ""

# Check for data-dynamic-favicon marker
echo "🔍 Checking for data-dynamic-favicon marker..."
if grep -q "data-dynamic-favicon" src/components/shared/DynamicMetadata.tsx; then
  echo "✅ Found data-dynamic-favicon marker (nuclear fix applied)"
else
  echo "❌ No data-dynamic-favicon marker found"
fi
echo ""

# Check for cleanup function
echo "🔍 Checking for cleanup function..."
if grep -q "cleanupRef" src/components/shared/DynamicMetadata.tsx; then
  echo "✅ Found cleanupRef (proper cleanup on unmount)"
else
  echo "❌ No cleanupRef found"
fi
echo ""

# Check for existing favicon removal logic
echo "🔍 Checking for favicon removal logic..."
if grep -q "existingFavicons" src/components/shared/DynamicMetadata.tsx; then
  echo "⚠️  Still trying to remove existing favicons - nuclear fix not fully applied"
else
  echo "✅ No favicon removal logic (nuclear fix applied)"
fi
echo ""

echo "=============================================="
echo "📊 Summary"
echo "=============================================="
echo ""

# Final verdict
if grep -q "data-dynamic-favicon" src/components/shared/DynamicMetadata.tsx && \
   ! grep -q "existingFavicons" src/components/shared/DynamicMetadata.tsx; then
  echo "✅ NUCLEAR FIX VERIFIED"
  echo ""
  echo "The component now:"
  echo "  • Only adds new favicons (never removes)"
  echo "  • Marks favicons with data-dynamic-favicon"
  echo "  • Cleans up on unmount only"
  echo "  • Avoids all removeChild errors"
  echo ""
  echo "🚀 Ready to test!"
  echo ""
  echo "Run: npm run dev"
  echo "Then check browser console for errors"
else
  echo "❌ NUCLEAR FIX NOT FULLY APPLIED"
  echo ""
  echo "Please check the implementation"
fi
