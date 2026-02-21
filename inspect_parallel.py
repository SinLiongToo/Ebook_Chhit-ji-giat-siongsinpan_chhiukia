
import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# count parallel containers
parallel_count = content.count('<div class="parallel-container">')
print(f"Total Parallel Containers: {parallel_count}")

# Find sections
sections = re.findall(r'<section id="(.*?)".*?>(.*?)</section>', content, re.DOTALL)
print(f"Total Sections: {len(sections)}")

failures = []
for sec_id, sec_content in sections:
    # Check for numbered paragraphs inside parallel containers (which is good)
    # But more importantly, check for numbered paragraphs OUTSIDE parallel containers
    
    # Remove all parallel containers from the section content to inspect what's left
    stripped_content = re.sub(r'<div class="parallel-container">.*?</div>', '[PARALLEL_REMOVED]', sec_content, flags=re.DOTALL)
    
    # Now look for numbered paragraphs in the remaining content
    num_matches = re.finditer(r'<p>\s*(\d+)\.?\s*</p>', stripped_content)
    nums = [int(m.group(1)) for m in num_matches]
    
    if len(nums) > 4: # If we see a sequence of numbers (e.g., 1, 2, 3...) outside parallel, it's suspicious
        # Check if they form a sequence
        is_sequence = False
        if 1 in nums and 2 in nums and 3 in nums:
            failures.append((sec_id, nums))

if failures:
    print("\nPotential Failures (numbered paragraphs not parallelized):")
    for sec_id, nums in failures:
        print(f"Section {sec_id}: Found numbers {nums[:10]}...")
else:
    print("\nNo obvious failures found (sequences like 1, 2, 3 outside parallel blocks).")

# Also, check if there are sections with NO parallel containers but arguably should have
print("\nSections with NO parallel containers:")
for sec_id, sec_content in sections:
    if '<div class="parallel-container">' not in sec_content:
        # Heuristic: does it have "1." and "2."?
        if "<p>1.</p>" in sec_content and "<p>2.</p>" in sec_content:
             print(f"Section {sec_id} has numbered paragraphs but no parallel container.")

