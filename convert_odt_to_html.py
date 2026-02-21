
"""
七字仔電子書 ODT 轉 HTML 轉換腳本
ODT to HTML Converter for Chhit-ji-a Ebook

此腳本用於將 LibreOffice/OpenOffice 的 ODT 文件轉換為適合 GitHub Pages 發佈的靜態 HTML 網頁。
主要功能包括：
1. 解析 ODT (XML) 內容結構。
2. 提取圖片並儲存至 images/ 資料夾。
3. 自動偵測「平行文本」(Parallel Text) 結構 (如：歌詞的漢字與羅馬字對照)，並將其轉換為左右並排的網頁佈局。
4. 產生側邊欄導覽 (Sidebar) 與章節內容。
5. 處理章節分割，特別是將「封面」、「序言」與後續章節分開。

Usage:
    python convert_odt_to_html.py
"""
import zipfile
import xml.etree.ElementTree as ET
import os
import shutil
import re
import html

ns = {
    'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
    'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
    'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
    'draw': 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0',
    'xlink': 'http://www.w3.org/1999/xlink',
}


def extract_text_and_images(elem, zip_ref, images_output_dir, footnotes=None):
    """
    從 ODT 元素中遞迴提取純文字與圖片。
    Recursively extracts text and handles image extraction from an ODT XML element.

    Args:
        elem (xml.etree.ElementTree.Element): 當前處理的 XML 元素。
        zip_ref (zipfile.ZipFile): 開啟的 ODT 壓縮檔物件 (用於提取圖片檔案)。
        images_output_dir (str): 圖片輸出的目標資料夾路徑。

    Returns:
        str: 該元素及其子元素包含的 HTML 格式文字內容 (包含 <img> 標籤)。
    """
    if footnotes is None:
        footnotes = []
    text_content = []
    
    if elem.text:
        text_content.append(html.escape(elem.text))
    
    for child in elem:
        tag = child.tag
        if tag == f"{{{ns['text']}}}s":
            count = int(child.attrib.get(f"{{{ns['text']}}}c", 1))
            text_content.append(" " * count)
        elif tag == f"{{{ns['text']}}}line-break":
            text_content.append("<br>")
        elif tag == f"{{{ns['text']}}}tab":
            text_content.append("&emsp;")
        elif tag == f"{{{ns['text']}}}span":
            text_content.append(extract_text_and_images(child, zip_ref, images_output_dir, footnotes))
        elif tag == f"{{{ns['draw']}}}frame":
            # Handle image
            draw_image = child.find(f"{{{ns['draw']}}}image", ns)
            if draw_image is not None:
                href = draw_image.attrib.get(f"{{{ns['xlink']}}}href")
                if href and href in zip_ref.namelist():
                    filename = os.path.basename(href)
                    t_path = os.path.join(images_output_dir, filename)
                    # Check if file already extracted to avoid rewrite
                    if not os.path.exists(t_path):
                        with open(t_path, "wb") as f_img:
                            f_img.write(zip_ref.read(href))
                    text_content.append(f'<img src="images/{filename}" class="book-image">')
        elif tag == f"{{{ns['text']}}}a":
             text_content.append(extract_text_and_images(child, zip_ref, images_output_dir, footnotes))
        elif tag == f"{{{ns['text']}}}note":
             note_citation = child.find(f"{{{ns['text']}}}note-citation", ns)
             citation_text = note_citation.text if note_citation is not None else "*"
             note_body = child.find(f"{{{ns['text']}}}note-body", ns)
             body_text = "".join(note_body.itertext()).strip() if note_body is not None else ""
             text_content.append(f'<sup class="footnote-marker">[{html.escape(citation_text)}]</sup>')
             footnotes.append(f'<span class="footnote-text">（註{html.escape(citation_text)}：{html.escape(body_text)}）</span>')
        
        if child.tail:
            text_content.append(html.escape(child.tail))
            
    return "".join(text_content)


def process_block_element(elem, zip_ref, images_dir):
    """
    處理區塊級元素 (Block-level elements)，如段落、標題、表格、列表等，將其轉換為 HTML。
    Converts ODT block elements (Heading, P, Table, List, Section) into HTML.

    Args:
        elem (xml.etree.ElementTree.Element): ODT XML 元素 (如 <text:p>, <text:h>)。
        zip_ref (zipfile.ZipFile): ODT 檔案物件。
        images_dir (str): 圖片儲存路徑。

    Returns:
        str: 轉換後的 HTML 字串。
    """
    html_parts = []
    tag = elem.tag
    
    if tag == f"{{{ns['text']}}}h":
         level = elem.attrib.get(f"{{{ns['text']}}}outline-level", "1")
         fns = []
         text = extract_text_and_images(elem, zip_ref, images_dir, fns)
         joined_fns = "".join([f"<br>{f}" for f in fns]) if fns else ""
         html_parts.append(f"<h{level}>{text}{joined_fns}</h{level}>")
         
    elif tag == f"{{{ns['text']}}}p":
         fns = []
         text = extract_text_and_images(elem, zip_ref, images_dir, fns)
         if text.strip() or "<img" in text:
             joined_fns = "".join([f"<br>{f}" for f in fns]) if fns else ""
             html_parts.append(f"<p>{text}{joined_fns}</p>")
             
    elif tag == f"{{{ns['table']}}}table":
         html_parts.append('<table>') 
         rows = elem.findall(f"{{{ns['table']}}}table-row", ns)
         
         for row in rows:
             cells = row.findall(f"{{{ns['table']}}}table-cell", ns)
             if not cells: continue
             
             html_parts.append('<tr>')
             for cell in cells:
                 # Process cell content (can have paragraphs, nested lists, etc)
                 cell_content = []
                 for child in cell:
                      cell_content.append(process_block_element(child, zip_ref, images_dir))
                 
                 cell_text = "".join(cell_content)
                 html_parts.append(f'<td>{cell_text}</td>')
             html_parts.append('</tr>')
             
         html_parts.append('</table>')
         
    elif tag == f"{{{ns['text']}}}section":
        # Capture children first
        section_children_html = []
        for child in elem:
            section_children_html.append(process_block_element(child, zip_ref, images_dir))
            
        # Analyze for parallel numbered lyrics
        processed_html = reorganize_section_content(section_children_html)
        html_parts.append(processed_html)
        
    elif tag == f"{{{ns['text']}}}list":
            html_parts.append("<ul>")
            for item in elem.findall(f"{{{ns['text']}}}list-item", ns):
                html_parts.append("<li>")
                for c in item:
                    html_parts.append(process_block_element(c, zip_ref, images_dir))
                html_parts.append("</li>")
            html_parts.append("</ul>")
    else:
             # Process children for unknown containers
             for child in elem:
                 html_parts.append(process_block_element(child, zip_ref, images_dir))

    return "".join(html_parts)

def reorganize_section_content(html_fragments):
    """
    重新組織章節內容，自動偵測並格式化「平行文本」(歌詞對照)。
    Analyzes HTML fragments to identify and format side-by-side parallel text (e.g., Lyrics).

    演算法核心邏輯：
    1. 尋找「編號段落」序列 (如: <p>1.</p> ... <p>1.</p>)。
    2. 若發現重複的編號序列 (例如: 1, 2, 3 ... 1, 2, 3)，則判定為平行文本。
    3. 將第一組 (1, 2, 3) 視為左欄 (例如漢字)，第二組 (1, 2, 3) 視為右欄 (例如羅馬字)。
    4. 使用 <div class="parallel-container"> 包裹，並透過 CSS Grid 進行排版。

    Args:
        html_fragments (list): 該章節內所有已經轉換為 HTML 的元素列表。

    Returns:
        str: 重新排版後的完整 HTML 字串。
    """
    # 1. Parse fragments into Items
    items = [] # List of {'html': str, 'number': int or None, 'type': 'number'|'content'}
    
    for frag in html_fragments:
        # Check if fragment is a numbered paragraph: <p>N.</p> or <p>N</p>
        # Relaxed check: <p>N.<br>...</p> or <p>N ...</p> to handle cases where content is in same paragraph
        match = re.search(r'^<p>\s*(\d+)\.?\s*</p>$', frag.strip())
        if not match:
            # Look for number followed by dot, space, or break tag
            match = re.search(r'^<p>\s*(\d+)(?:[\.\s]|<br\s*/?>)', frag.strip())
            
        if match:
            items.append({'html': frag, 'number': int(match.group(1)), 'type': 'number'})
        else:
            items.append({'html': frag, 'number': None, 'type': 'content'})
            
    # 2. Identify indices of numbered items
    numbers_indices = [i for i, x in enumerate(items) if x['type'] == 'number']
    nums = [items[i]['number'] for i in numbers_indices]
    
    if not nums:
        return "".join(html_fragments)

    # 3. Iterate through numbers to find parallel sequences
    result_html = []
    current_num_idx = 0
    processed_item_idx = 0
    
    while current_num_idx < len(nums):
        remaining_len = len(nums) - current_num_idx
        found_match = False
        best_k = 0
        
        # Look for the longest repeating sequence: [A]...[A]
        # Try k from max possible down to 1
        max_k = remaining_len // 2
        
        for k in range(max_k, 0, -1):
            seq1 = nums[current_num_idx : current_num_idx + k]
            seq2 = nums[current_num_idx + k : current_num_idx + 2*k]
            if seq1 == seq2:
                best_k = k
                found_match = True
                break
        
        if found_match:
            # We found a parallel block of length k
            
            # A. Append any content occurring *before* this block starts
            start_item_idx = numbers_indices[current_num_idx]
            if processed_item_idx < start_item_idx:
                chunk = items[processed_item_idx : start_item_idx]
                result_html.append("".join(x['html'] for x in chunk))
            
            # B. Construct the Parallel Container
            result_html.append('<div class="parallel-container">')
            
            for i in range(best_k):
                # Left Column Chunk
                l_idx_in_nums = current_num_idx + i
                l_item_start = numbers_indices[l_idx_in_nums]
                l_item_end = numbers_indices[l_idx_in_nums + 1] # Start of next number
                
                # Right Column Chunk
                r_idx_in_nums = current_num_idx + best_k + i
                r_item_start = numbers_indices[r_idx_in_nums]
                
                # For the right chunk's end:
                if r_idx_in_nums + 1 < len(numbers_indices):
                    r_item_end = numbers_indices[r_idx_in_nums + 1]
                else:
                    # If this is the very last number, consume until end of items
                    r_item_end = len(items)
                
                left_chunk_html = "".join(x['html'] for x in items[l_item_start : l_item_end])
                right_chunk_html = "".join(x['html'] for x in items[r_item_start : r_item_end])
                
                result_html.append('<div class="stanza-row">')
                result_html.append(f'<div class="stanza-col">{left_chunk_html}</div>')
                result_html.append(f'<div class="stanza-col">{right_chunk_html}</div>')
                result_html.append('</div>')
            
            result_html.append('</div>')
            
            # C. Update state
            # Next processed item should be r_item_end of the last pair
            last_r_idx = current_num_idx + 2 * best_k - 1
            if last_r_idx + 1 < len(numbers_indices):
                processed_item_idx = numbers_indices[last_r_idx + 1]
            else:
                processed_item_idx = len(items)
                
            current_num_idx += 2 * best_k
            
        else:
            # No match found. Treat this number block as normal content.
            
            # A. Append gap content + this number content
            start_item_idx = numbers_indices[current_num_idx]
            
            if current_num_idx + 1 < len(numbers_indices):
                end_item_idx = numbers_indices[current_num_idx + 1]
            else:
                end_item_idx = len(items)
            
            # We output everything from processed_item_idx up to the end of this number block
            if processed_item_idx < end_item_idx:
                chunk = items[processed_item_idx : end_item_idx]
                result_html.append("".join(x['html'] for x in chunk))
            
            processed_item_idx = end_item_idx
            current_num_idx += 1
            
    # 4. Append any trailing content after the last number
    if processed_item_idx < len(items):
        chunk = items[processed_item_idx:]
        result_html.append("".join(x['html'] for x in chunk))

    return "".join(result_html)


def convert_odt(odt_file, web_book_dir):
    """
    主轉換函數：讀取 ODT，解析結構，並生成最終的 index.html。
    Main conversion function.

    流程 (Workflow):
    1. 解壓縮 ODT 檔案至暫存區。
    2. 解析 content.xml 取得文件內容。
    3. 遍歷主要內容 (body)，依據標題 (Heading) 進行章節分割。
    4. 應用啟發式邏輯 (Heuristic) 判斷章節邊界 (例如分離封面與序言)。
    5. 對每個章節呼叫 `reorganize_section_content` 進行排版優化。
    6. 生成包含側邊欄 (Sidebar) 的完整 HTML 檔案。

    Args:
        odt_file (str): 來源 ODT 檔案路徑。
        web_book_dir (str): 網頁輸出的根目錄 (包含 index.html 和 images/)。
    """
    temp_dir = "temp_odt_extract"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    images_dir = os.path.join(web_book_dir, "images")
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        
    output_html = os.path.join(web_book_dir, "index.html")
    
    try:
        with zipfile.ZipFile(odt_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            content_xml = os.path.join(temp_dir, "content.xml")
            
            tree = ET.parse(content_xml)
            root = tree.getroot()
            body = root.find('.//office:body/office:text', ns)
            
            sidebar_items = []
            sections_html = []
            
            if body is not None:
                current_group_fragments = []
                current_title = "封面"
                current_id_index = 0
                
                for child in body:
                    tag = child.tag
                    
                    # Case 1: Top-level Heading -> Start new section
                    if tag == f"{{{ns['text']}}}h":
                        if current_group_fragments:
                            # Close previous accumulated content (e.g. preface or content between sections)
                            processed_html = reorganize_section_content(current_group_fragments)
                            
                            sec_id = f"section-{current_id_index}"
                            active_class = " active" if current_id_index == 0 else ""
                            sections_html.append(f'<section id="{sec_id}" class="book-section{active_class}">{processed_html}</section>')
                            sidebar_items.append({'id': sec_id, 'title': current_title})
                            
                            current_id_index += 1
                            current_group_fragments = []
                            
                        # Process this heading and start a new accumulation
                        h_html = process_block_element(child, zip_ref, images_dir)
                        current_group_fragments.append(h_html)
                        
                        # Extract title from this heading
                        title_text = re.sub(r'<[^>]+>', '', h_html).strip()
                        current_title = title_text if title_text else f"Section {current_id_index}"
                        
                    # Case 2: Explicit Text Section -> Treat as a standalone section, but merge if previous was just a header
                    elif tag == f"{{{ns['text']}}}section":
                         sec_html_full = process_block_element(child, zip_ref, images_dir)
                         if not sec_html_full.strip(): continue
                         
                         # Determine if we should split into multiple sections
                         sec_chunks = []
                         # Heuristic: If one ODT section contains multiple non-empty H1/H2 headings,
                         # it likely actually contains multiple conceptual sections.
                         matches = list(re.finditer(r'(<h[1-2][^>]*>(.*?)</h[1-2]>)', sec_html_full, re.IGNORECASE | re.DOTALL))
                         non_empty_indices = []
                         for i, m in enumerate(matches):
                             h_content = m.group(2)
                             if re.sub(r'<[^>]+>', '', h_content).strip():
                                 non_empty_indices.append(m.start())
                         
                         if len(non_empty_indices) > 1:
                             current_pos = 0
                             for i in range(1, len(non_empty_indices)):
                                 split_pos = non_empty_indices[i]
                                 sec_chunks.append(sec_html_full[current_pos:split_pos])
                                 current_pos = split_pos
                             if current_pos < len(sec_html_full):
                                 sec_chunks.append(sec_html_full[current_pos:])
                         
                         if not sec_chunks:
                             sec_chunks = [sec_html_full]
                             
                         for section_chunk_idx, sec_html in enumerate(sec_chunks):
                             # Determine if we should split from the current accumulation
                             should_split = True
                             if current_group_fragments:
                                 # 啟發式邏輯 (Heuristic):
                                 # 如果當前累積的內容看起來只是一個標題 (長度短且無圖片)，則選擇合併 (MERGE)。
                                 # 如果累積內容相當充實 (例如封面、圖片、或前一章節的文字)，則強制分割 (SPLIT)。
                                 # Heuristic: If current buffer looks like just a Heading (short, no images), MERGE.
                                 # If it is substantial (Cover, Images, previous text), SPLIT.
                                 combined_txt = "".join(current_group_fragments)
                                 has_img = "<img" in combined_txt
                                 is_short = len(combined_txt) < 300
                                 
                                 if is_short and not has_img:
                                     should_split = False
                                 
                                 # Force split if this is a sub-chunk (splitting within one ODT section)
                                 if section_chunk_idx > 0:
                                     should_split = True
                                     
                                 # Force split if the NEW section contains a non-empty heading
                                 temp_titles = re.findall(r'<h[1-2][^>]*>(.*?)</h[1-2]>', sec_html, re.I | re.DOTALL)
                                 if any(re.sub(r'<[^>]+>', '', t).strip() for t in temp_titles):
                                     should_split = True

                                 # Force merge for specific titles like Table of Contents
                                 if "目錄" in current_title and "寫作日期" in current_title:
                                     should_split = False

                             if should_split:
                                processed_html = reorganize_section_content(current_group_fragments)
                                
                                sec_id = f"section-{current_id_index}"
                                active_class = " active" if current_id_index == 0 else ""
                                sections_html.append(f'<section id="{sec_id}" class="book-section{active_class}">{processed_html}</section>')
                                sidebar_items.append({'id': sec_id, 'title': current_title})
                                
                                current_id_index += 1
                                current_group_fragments = []
                                # For the new group, we need to extract a title from the section content if possible
                                # Find all headings
                                title_matches = re.findall(r'<h[1-2][^>]*>(.*?)</h[1-2]>', sec_html, re.IGNORECASE)
                                found_title = False
                                for t_html in title_matches:
                                    clean_t = re.sub(r'<[^>]+>', '', t_html).strip()
                                    if clean_t:
                                        current_title = clean_t
                                        found_title = True
                                        break
                                
                                if not found_title:
                                    clean_text = re.sub(r'<[^>]+>', '', sec_html).strip()
                                    current_title = clean_text[:20] + "..." if clean_text else f"Section {current_id_index}"
                             
                             # Check for Copyright Split within EACH chunk
                             if ("書名：Chhit-jī-gi̍at" in sec_html or "書名：" in sec_html) and ("目錄" in current_title or current_id_index >= 45):
                                 # Find split point
                                 split_token = "書名："
                                 if "書名：Chhit-jī-gi̍at" in sec_html: split_token = "書名：Chhit-jī-gi̍at"
                                 
                                 # Attempt regex split
                                 pattern = r'(<p[^>]*>\s*' + re.escape(split_token) + r'.*?</p>)'
                                 parts = re.split(pattern, sec_html, 1, re.DOTALL)
                                 
                                 if len(parts) >= 2:
                                     p1 = parts[0]
                                     copyright_content = parts[1] + (parts[2] if len(parts) > 2 else "")
                                     
                                     # Check if p1 ends with an image paragraph
                                     img_match = re.search(r'(<p[^>]*>\s*<img[^>]+>\s*</p>)\s*$', p1, re.DOTALL)
                                     if img_match:
                                         img_html = img_match.group(1)
                                         p1 = p1[:img_match.start(1)]
                                         copyright_content = img_html + copyright_content
                                     
                                     current_group_fragments.append(p1)
                                     processed_html = reorganize_section_content(current_group_fragments)
                                     sec_id = f"section-{current_id_index}"
                                     active_class = " active" if current_id_index == 0 else ""
                                     sections_html.append(f'<section id="{sec_id}" class="book-section{active_class}">{processed_html}</section>')
                                     sidebar_items.append({'id': sec_id, 'title': current_title})
                                     
                                     current_id_index += 1
                                     current_group_fragments = []
                                     current_title = "版權頁"
                                     current_group_fragments.append(copyright_content)
                                 else:
                                     current_group_fragments.append(sec_html)
                             else:
                                 current_group_fragments.append(sec_html)
                         # If we merged, we keep the existing current_title (which came from the Heading likely)
                         
                    # Case 3: Other content (P, Table, etc.) -> Add to current accumulation
                    else:
                        child_html = process_block_element(child, zip_ref, images_dir)
                        if child_html.strip():
                             # Special check for Copyright Page split
                             # User requested copyright page to be separate (it follows the last image of TOC)
                             if ("書名：Chhit-jī-gi̍at" in child_html or "書名：" in child_html) and ("目錄" in current_title or current_id_index >= 45):
                                  # Force a split here - Flush previous content (TOC)
                                  
                                  # Check if the last fragment is an image (move it to copyright page)
                                  last_frag_img = None
                                  if current_group_fragments:
                                      last_frag = current_group_fragments[-1]
                                      # Check for image tag
                                      if "<img" in last_frag:
                                           # If it looks like a standalone image paragraph
                                           if re.search(r'^<p>\s*<img[^>]+>\s*</p>$', last_frag.strip()):
                                                last_frag_img = current_group_fragments.pop()
                                  
                                  processed_html = reorganize_section_content(current_group_fragments)
                                  sec_id = f"section-{current_id_index}"
                                  active_class = " active" if current_id_index == 0 else ""
                                  sections_html.append(f'<section id="{sec_id}" class="book-section{active_class}">{processed_html}</section>')
                                  sidebar_items.append({'id': sec_id, 'title': current_title})
                                  
                                  current_id_index += 1
                                  current_group_fragments = []
                                  current_title = "版權頁" # Set new title for Copyright Page
                                  
                                  if last_frag_img:
                                      current_group_fragments.append(last_frag_img)
                             
                             current_group_fragments.append(child_html)
                             
                # End of loop: wrap up the last group
                if current_group_fragments:
                     print(f"Final section {current_id_index}. Fragment count: {len(current_group_fragments)}")
                     processed_html = reorganize_section_content(current_group_fragments)
                     sec_id = f"section-{current_id_index}"
                     active_class = " active" if current_id_index == 0 else ""
                     sections_html.append(f'<section id="{sec_id}" class="book-section{active_class}">{processed_html}</section>')
                     sidebar_items.append({'id': sec_id, 'title': current_title})

            else:
                sections_html.append("<p>Error: No body found.</p>")

        # Generate Sidebar HTML
        sidebar_html = '<ul>'
        for item in sidebar_items:
            # Clean title
            t = item["title"]
            if len(t) > 20: t = t[:20] + "..."
            sidebar_html += f'<li class="nav-item" data-target="{item["id"]}">{t}</li>'
        sidebar_html += '</ul>'

        full_html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>七字仔 - 電子書</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Klee+One&family=Noto+Serif+TC:wght@400;700&family=Roboto:wght@400;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="app-container">
        <nav class="sidebar" id="sidebar">
            <div class="sidebar-header">目錄</div>
            {sidebar_html}
        </nav>
        <div class="overlay" id="sidebar-overlay"></div>
        <main class="content">
            <div class="mobile-header">
                <button id="menu-toggle" class="menu-toggle">☰ 目錄</button>
            </div>
            { "".join(sections_html) }
        </main>
    </div>
    <script src="script.js"></script>
</body>
</html>
"""
        with open(output_html, "w", encoding="utf-8") as f:
            f.write(full_html)
            
        print(f"Converted to {output_html}")
        
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    odt_filename = "merged_2026_2_6_ relayout_ISBN_封面修_目錄修_二校.odt"
    web_dir = "docs"
    if not os.path.exists(web_dir):
        os.makedirs(web_dir)
    convert_odt(odt_filename, web_dir)
