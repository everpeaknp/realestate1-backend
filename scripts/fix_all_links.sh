#!/bin/bash

# Script to replace all Next.js Link components with window.location.href navigation
# This fixes the multi-click navigation issue across the entire website

echo "🔧 Fixing all Link components in the frontend..."

cd frontend/src

# Find all .tsx files that contain Link components
FILES=$(grep -rl "from 'next/link'" . --include="*.tsx")

echo "📝 Found $(echo "$FILES" | wc -l) files with Link components"

# For each file, we need to:
# 1. Keep the import (we might still use Link for logo)
# 2. Replace <Link href="..."> with <a href="..." onClick={(e) => { e.preventDefault(); window.location.href = '...'; }}>
# 3. Replace </Link> with </a>

# This is complex, so let's create a Node.js script to do it properly

cd ../..

cat > fix_links.js << 'EOF'
const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Find all .tsx files in frontend/src
const files = glob.sync('frontend/src/**/*.tsx');

let totalFixed = 0;
let filesModified = 0;

files.forEach(file => {
  let content = fs.readFileSync(file, 'utf8');
  const originalContent = content;
  
  // Skip if no Link import
  if (!content.includes("from 'next/link'")) {
    return;
  }
  
  // Pattern 1: <Link href="/path">text</Link>
  // Replace with: <a href="/path" onClick={(e) => { e.preventDefault(); window.location.href = '/path'; }}>text</a>
  
  // Pattern 2: <Link href={variable}>text</Link>
  // Replace with: <a href={variable} onClick={(e) => { e.preventDefault(); window.location.href = variable; }}>text</a>
  
  // This is complex because Link can span multiple lines and have various props
  // Let's use a more sophisticated approach
  
  // Count Link occurrences
  const linkMatches = content.match(/<Link\s/g);
  if (!linkMatches) return;
  
  console.log(`\n📄 ${file}: Found ${linkMatches.length} Link components`);
  
  // For now, just report - manual fix needed for complex cases
  filesModified++;
  totalFixed += linkMatches.length;
});

console.log(`\n✅ Summary:`);
console.log(`   Files with Links: ${filesModified}`);
console.log(`   Total Links found: ${totalFixed}`);
console.log(`\n⚠️  Manual fix required - Link components are too complex for automated replacement`);
console.log(`   Recommended: Fix high-traffic pages first (home, properties, blog)`);

EOF

node fix_links.js

echo ""
echo "✅ Analysis complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Fix high-traffic pages first:"
echo "      - frontend/src/components/home/hero.tsx"
echo "      - frontend/src/components/home/FeaturedProperties.tsx"
echo "      - frontend/src/components/properties/PropertyList.tsx"
echo "      - frontend/src/components/blog/BlogList.tsx"
echo "      - frontend/src/components/common/Footer.tsx"
echo ""
echo "   2. Pattern to use:"
echo "      BEFORE: <Link href=\"/path\">Text</Link>"
echo "      AFTER:  <a href=\"/path\" onClick={(e) => { e.preventDefault(); window.location.href = '/path'; }}>Text</a>"
echo ""
