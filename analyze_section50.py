
import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract Section 50
match = re.search(r'<section id="section-50".*?</section>', content, re.DOTALL)
if match:
    sec_content = match.group(0)
    with open('section50_dump.txt', 'w', encoding='utf-8') as out:
        out.write("--- SECTION 50 CONTENT SUMMARY ---\n")
        out.write(f"Total length: {len(sec_content)}\n")
        
        # Check for images
        imgs = re.findall(r'<img[^>]+>', sec_content)
        out.write(f"Found {len(imgs)} images in Section 50.\n")
        for i, img in enumerate(imgs):
            out.write(f"Image {i+1}: {img}\n")
            
        # Check for "Copyright" or "版權" text
        if "版權" in sec_content:
            out.write("Found '版權' in section.\n")
        if "Copyright" in sec_content:
            out.write("Found 'Copyright' in section.\n")
            
        # Print the end of the section content
        out.write("\n--- END OF SECTION 50 ---\n")
        out.write(sec_content[-1000:])
else:
    print("Section 50 not found.")
