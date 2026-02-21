
import zipfile

def extract_snippet(odt_file):
    with zipfile.ZipFile(odt_file, 'r') as z:
        with z.open('content.xml') as f:
            content = f.read()
            body_start = content.find(b'<office:body>')
            if body_start != -1:
                with open("debug_output.xml", "wb") as out:
                    out.write(content[body_start:body_start+4000])
            else:
                with open("debug_output.xml", "w") as out:
                    out.write("office:body not found")

if __name__ == "__main__":
    extract_snippet("merged_2026_2_6_ relayout_ISBN_封面修_目錄修_二校.odt")
