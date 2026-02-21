import zipfile
import xml.etree.ElementTree as ET
import sys
sys.stdout.reconfigure(encoding='utf-8')

import xml.etree.ElementTree as ET

odt_file = "merged_2026_2_6_ relayout_ISBN_封面修_目錄修_二校.odt"
ns = {
    'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
    'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
}

with zipfile.ZipFile(odt_file, 'r') as z:
    with z.open('content.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        notes = root.findall('.//text:note', ns)
        
        print(f"Total notes found: {len(notes)}")
        for i, note in enumerate(notes[:5]):
            note_class = note.attrib.get(f"{{{ns['text']}}}note-class")
            citation = note.find('.//text:note-citation', ns)
            citation_text = citation.text if citation is not None else ""
            body = note.find('.//text:note-body', ns)
            body_text = "".join(body.itertext()) if body is not None else ""
            
            print(f"Note {i}: class={note_class}, citation={citation_text}, text={body_text}")
