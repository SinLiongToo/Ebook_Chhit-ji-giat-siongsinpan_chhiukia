
import sys
import codecs

with open('docs/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find Section 37 content to check title
idx = content.find('id="section-38"')
if idx != -1:
    with open('section38_result_dump.txt', 'w', encoding='utf-8') as out:
         out.write(content[idx:idx+500])
else:
    with open('section38_result_dump.txt', 'w', encoding='utf-8') as out:
         out.write("Section 38 NOT FOUND")
