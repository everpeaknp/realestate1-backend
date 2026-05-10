#!/bin/bash

# Hydration Fix Verification Script
# Run this after applying the hydration fixes

echo "🔍 Verifying Hydration Fixes..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: Verify no unsafe .remove() calls
echo "1️⃣  Checking for unsafe .remove() calls..."
REMOVE_COUNT=$(grep -r "\.remove()" src/ --include="*.tsx" --include="*.ts" 2>/dev/null | wc -l)
if [ "$REMOVE_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ No unsafe .remove() calls found${NC}"
else
    echo -e "${RED}❌ Found $REMOVE_COUNT .remove() calls - review these:${NC}"
    grep -rn "\.remove()" src/ --include="*.tsx" --include="*.ts"
fi
echo ""

# Check 2: Verify DynamicMetadata has SSR check
echo "2️⃣  Checking DynamicMetadata component..."
if grep -q "typeof window === 'undefined'" src/components/shared/DynamicMetadata.tsx 2>/dev/null; then
    echo -e "${GREEN}✅ DynamicMetadata has SSR check${NC}"
else
    echo -e "${RED}❌ DynamicMetadata missing SSR check${NC}"
fi
echo ""

# Check 3: Verify TawkToChat has safe cleanup
echo "3️⃣  Checking TawkToChat component..."
if grep -q "parentNode.removeChild" src/components/chatbot/TawkToChat.tsx 2>/dev/null; then
    echo -e "${GREEN}✅ TawkToChat uses safe cleanup${NC}"
else
    echo -e "${RED}❌ TawkToChat missing safe cleanup${NC}"
fi
echo ""

# Check 4: Verify LazyImage has client-side error logging
echo "4️⃣  Checking LazyImage component..."
if grep -q "typeof window !== 'undefined'" src/components/shared/LazyImage.tsx 2>/dev/null; then
    echo -e "${GREEN}✅ LazyImage has client-side checks${NC}"
else
    echo -e "${YELLOW}⚠️  LazyImage might need client-side checks${NC}"
fi
echo ""

# Check 5: Look for potential hydration issues
echo "5️⃣  Scanning for potential hydration issues..."
ISSUES=0

# Check for window access outside useEffect
WINDOW_ACCESS=$(grep -r "window\." src/ --include="*.tsx" --include="*.ts" | grep -v "useEffect" | grep -v "typeof window" | grep -v "// " | wc -l)
if [ "$WINDOW_ACCESS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $WINDOW_ACCESS potential window access outside useEffect${NC}"
    ISSUES=$((ISSUES + 1))
fi

# Check for document access outside useEffect
DOC_ACCESS=$(grep -r "document\." src/ --include="*.tsx" --include="*.ts" | grep -v "useEffect" | grep -v "typeof window" | grep -v "// " | wc -l)
if [ "$DOC_ACCESS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $DOC_ACCESS potential document access outside useEffect${NC}"
    ISSUES=$((ISSUES + 1))
fi

# Check for localStorage access outside useEffect
STORAGE_ACCESS=$(grep -r "localStorage\." src/ --include="*.tsx" --include="*.ts" | grep -v "useEffect" | grep -v "typeof window" | grep -v "// " | wc -l)
if [ "$STORAGE_ACCESS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $STORAGE_ACCESS potential localStorage access outside useEffect${NC}"
    ISSUES=$((ISSUES + 1))
fi

if [ "$ISSUES" -eq 0 ]; then
    echo -e "${GREEN}✅ No obvious hydration issues found${NC}"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Verification Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$REMOVE_COUNT" -eq 0 ] && [ "$ISSUES" -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Hydration fixes look good.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run: npm run dev"
    echo "2. Open browser console"
    echo "3. Check for hydration warnings"
    echo "4. Test all pages"
else
    echo -e "${YELLOW}⚠️  Some issues found. Review the output above.${NC}"
fi

echo ""
echo "📚 Documentation:"
echo "   - HYDRATION_ERROR_FIXED.md"
echo "   - doc/HYDRATION_FIX_2026-05-09.md"
echo "   - doc/HYDRATION_QUICK_FIX_GUIDE.md"
echo ""
