
import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Locate 10. inside Section 2
match = re.search(r'<section id="section-2".*?(<p>\s*10\..*?)</section>', content, re.DOTALL)
if match:
    snippet = match.group(1)
    with open('check_fix_report.txt', 'w', encoding='utf-8') as out:
         out.write("Found 10. in Section 2:\n")
         out.write(snippet[:500])
         out.write("\n\n--- Context around 10. ---\n")
         start = content.find('<p>10.', content.find('id="section-2"'))
         out.write(content[start-200:start+200])
else:
    print("Could not find '10.' in Section 2")
