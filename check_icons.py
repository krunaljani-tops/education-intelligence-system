import os
import re

src_dir = 'frontend/src'
icons = set()
for root, dirs, files in os.walk(src_dir):
    for f in files:
        if f.endswith('.jsx'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8') as file:
                content = file.read()
                matches = re.findall(r'import\s+\{([^}]+)\}\s+from\s+[\'\"]lucide-react[\'\"]', content)
                for m in matches:
                    for icon in m.split(','):
                        icon = icon.strip()
                        if icon:
                            icons.add(icon)
print(f'Total unique lucide icons: {len(icons)}')
print(sorted(list(icons)))

# Test importing with Node
import subprocess
node_code = f"""
import * as Lucide from 'lucide-react';
const icons = {list(icons)};
const missing = icons.filter(i => !Lucide[i]);
console.log('Missing icons in lucide-react:', missing);
"""
with open('test_icons.mjs', 'w') as f:
    f.write(node_code)

res = subprocess.run(["node", "test_icons.mjs"], cwd="frontend", capture_output=True, text=True)
print("Node output:", res.stdout, res.stderr)
