
import sys
import codecs

with open('docs/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find Section 2
import re
match = re.search(r'<section id="section-2"(.*?)>(.*?)</section>', content, re.DOTALL)
if match:
    start_idx = match.start(2)
    end_idx = match.end(2)
    # Get a chunk around the middle/end where usually items 9+ happen
    chunk = content[start_idx:end_idx][-4000:] 
    
    with open('section2_dump.txt', 'w', encoding='utf-8') as out:
         out.write(chunk)
else:
    with open('section2_dump.txt', 'w', encoding='utf-8') as out:
        out.write("Section 2 NOT FOUND")
