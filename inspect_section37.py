
import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find Section 37
import re
match = re.search(r'<section id="section-37"(.*?)>(.*?)</section>', content, re.DOTALL)
if match:
    sec_content = match.group(2)
    with open('section37_dump.txt', 'w', encoding='utf-8') as out:
        out.write("--- SECTION 37 CONTENT ---\n")
        out.write(sec_content[:2000])
else:
    with open('section37_dump.txt', 'w', encoding='utf-8') as out:
        out.write("Section 37 NOT FOUND")
