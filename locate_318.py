
import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

sections = re.findall(r'<section id="(.*?)" class="book-section.*?">(.*?)</section>', content, re.DOTALL)

for sid, scontent in sections:
    if "服貿318" in scontent:
         print(f"Found '服貿318' in {sid}")
         # Find titles in this section
         titles = re.findall(r'<h[1-2][^>]*>(.*?)</h[1-2]>', scontent, re.IGNORECASE)
         print(f"Titles in {sid}: {titles}")
