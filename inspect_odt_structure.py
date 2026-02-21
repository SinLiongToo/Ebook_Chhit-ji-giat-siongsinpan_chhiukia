
import zipfile
import xml.etree.ElementTree as ET
import os

odt_file = "merged_2026_2_6_ relayout_ISBN_封面修_目錄修_二校.odt"
ns = {
    'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
    'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
    'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
    'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0'
}

with zipfile.ZipFile(odt_file, 'r') as z:
    with z.open('content.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        body = root.find('.//office:body/office:text', ns)
        
        print("Top level elements in body:")
        count = 0
        for child in body:
            count += 1
            if count > 20: break
            
            
            # Get text content snippet
            text_content = "".join(child.itertext())[:50].replace("\n", " ")
            tag_name = child.tag.replace(f"{{{ns['text']}}}", "text:")
            
            # Search for "序 "
            if "序" in text_content and "台灣RAP" in text_content:
                print(f"FOUND PREFACE! Tag: {tag_name}")
                print(f"Parent: Body? {child in body}")
                
            try:
                print(f"{tag_name}: {text_content}".encode("utf-8", "replace").decode("utf-8"))
            except:
                pass
            
            if tag_name == "text:h":
                print(f"   (Heading Level: {child.get(f'{{{ns['text']}}}outline-level')})")
