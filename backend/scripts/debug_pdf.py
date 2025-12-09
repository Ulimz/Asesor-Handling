
import os
from pypdf import PdfReader

DATA_DIR = "/app/data/real"

def inspect_pdf(filename):
    pdf_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    print(f"--- Inspecting {filename} ---")
    reader = PdfReader(pdf_path)
    # Print first 5 pages to see the structure
    for i in range(min(5, len(reader.pages))):
        print(f"--- PAGE {i+1} ---")
        print(reader.pages[i].extract_text())
        print("\n")

if __name__ == "__main__":
    # inspect_pdf("Iberia_XXII_Convenio.pdf")
    inspect_pdf("Swissport_Convenio.pdf")
