import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Preformatted, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# ---- CONFIG ----
SOURCE_FOLDER = "../knowledge_base/Wolfenstein3D_Clone"
OUTPUT_PDF = "codebase_dump.pdf"
CODE_EXTENSIONS = {".cpp", ".hpp", ".h", ".c", ".cc", ".cxx", ".py", ".js", ".ts"}
EXCLUDE_DIRS = {"build", "third_party", "deps", "vendor", ".git", "node_modules", "venv"}
MAX_FILE_SIZE_MB = 2  # skip huge files

styles = getSampleStyleSheet()
header_style = ParagraphStyle(
    "FileHeader", parent=styles["Heading2"],
    textColor="#1a1a1a", spaceAfter=6
)
code_style = ParagraphStyle(
    "Code", fontName="Courier", fontSize=7, leading=9
)

def collect_files(root):
    matches = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fname in filenames:
            if os.path.splitext(fname)[1].lower() in CODE_EXTENSIONS:
                full_path = os.path.join(dirpath, fname)
                matches.append(full_path)
    return sorted(matches)

def build_pdf(root, output_path):
    story = []
    files = collect_files(root)
    story.append(Paragraph(f"Codebase Dump: {os.path.basename(root)}", styles["Title"]))
    story.append(Paragraph(f"{len(files)} files", styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    for path in files:
        rel_path = os.path.relpath(path, root)
        size_mb = os.path.getsize(path) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            continue

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            content = f"[Could not read file: {e}]"

        story.append(Paragraph(rel_path, header_style))
        story.append(Preformatted(content, code_style))
        story.append(PageBreak())

    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        topMargin=0.6*inch, bottomMargin=0.6*inch,
        leftMargin=0.6*inch, rightMargin=0.6*inch
    )
    doc.build(story)
    print(f"Wrote {len(files)} files to {output_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(script_dir, SOURCE_FOLDER))
    output_path = os.path.abspath(os.path.join(script_dir, OUTPUT_PDF))
    build_pdf(root, output_path)