import zipfile
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
        # Find the first paragraph containing a note
        for p in root.findall('.//text:p', ns):
            if p.find('.//text:note', ns) is not None:
                # dump the XML of this paragraph
                xml_str = ET.tostring(p, encoding='unicode')
                with open('note_dump.txt', 'w', encoding='utf-8') as out_f:
                    out_f.write(xml_str)
                break
