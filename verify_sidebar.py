
import sys
import codecs

with open('docs/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the sidebar navigation items
import re
nav_items = re.findall(r'<li class="nav-item" data-target="(.*?)">(.*?)</li>', content)

with open('sidebar_check.txt', 'w', encoding='utf-8') as out:
    for target, label in nav_items:
        out.write(f"{target}: {label}\n")

# Just print success message
print("Sidebar labels written to sidebar_check.txt successfully.")
