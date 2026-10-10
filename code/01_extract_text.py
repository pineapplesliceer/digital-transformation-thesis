from pipeline_utils import RAW, TEXT, parse_report_name
from pathlib import Path

def extract_pdf(pdf_path):
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise SystemExit("Missing pypdf. Run: pip install -r requirements.txt") from e
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)

def main():
    pdfs = sorted(RAW.glob("*.pdf"))
    if not pdfs:
        print("No PDFs found. DEMO mode can still run from the supplied panel data.")
        print("For real reports, place files in raw_reports/ named like 000001_2024.pdf.")
        return
    ok = 0
    for p in pdfs:
        try:
            firm, year = parse_report_name(p)
            text = extract_pdf(p)
            if len(text.strip()) < 500:
                print(f"WARNING: {p.name} extracted little text; it may be a scanned PDF and require OCR.")
            (TEXT/f"{firm}_{year}.txt").write_text(text, encoding="utf-8")
            ok += 1
        except Exception as e:
            print("FAILED", p.name, e)
    print(f"Extracted {ok}/{len(pdfs)} reports.")

if __name__ == "__main__":
    main()
