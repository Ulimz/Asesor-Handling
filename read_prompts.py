
import zipfile
import re
import os
import xml.etree.ElementTree as ET

def get_docx_text(path):
    try:
        with zipfile.ZipFile(path) as document:
            xml_content = document.read('word/document.xml')
            
            # Remove namespaces for easier parsing (naive but effective for text extraction)
            xml_str = xml_content.decode('utf-8')
            xml_str = re.sub(r' xmlns:[\w-]+="[^"]+"', '', xml_str) # Remove declaration
            xml_str = re.sub(r' \w+:', ' ', xml_str) # Remove prefixes in attributes
            xml_str = re.sub(r'<\w+:', '<', xml_str) # Remove prefixes in tags
            xml_str = re.sub(r'</\w+:', '</', xml_str) # Remove prefixes in closing tags
            
            tree = ET.fromstring(xml_str)
            
            text_parts = []
            for elem in tree.iter():
                if elem.tag == 't' and elem.text:
                    text_parts.append(elem.text)
                elif elem.tag == 'br' or elem.tag == 'p':
                    text_parts.append('\n')
            
            return ''.join(text_parts)
    except Exception as e:
        return f"Error reading {path}: {str(e)}"

import glob

base_path = r"C:\Users\ulise\Programas Uli\Asistente_Handling\Prompts"
files = glob.glob(os.path.join(base_path, "*.docx"))

print("--- START EXTRACT ---")
if not files:
    print(f"No .docx files found in {base_path}")

for full_path in files:
    filename = os.path.basename(full_path)
    print(f"### FILE: {filename}")
    print(get_docx_text(full_path))
    print("\n--- END FILE ---\n")
