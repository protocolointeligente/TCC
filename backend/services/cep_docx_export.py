from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH


def _add_text_block(document: Document, heading: str, content: str) -> None:
    document.add_heading(heading, level=1)
    for paragraph in content.split("\n"):
        if paragraph.strip():
            p = document.add_paragraph(paragraph.strip())
            p.paragraph_format.first_line_indent = Cm(1.25)
            p.paragraph_format.line_spacing = 1.5
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def export_cep_project_to_docx(project, filename: str) -> str:
    document = Document()

    for section in document.sections:
        section.top_margin = Cm(3)
        section.left_margin = Cm(3)
        section.bottom_margin = Cm(2)
        section.right_margin = Cm(2)

    normal = document.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)

    title = document.add_heading(project.title, level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    _add_text_block(document, "Projeto de Pesquisa", project.generated_project or "")

    document.add_page_break()
    _add_text_block(document, "TCLE — Termo de Consentimento Livre e Esclarecido", project.tcle or "")

    if project.tale and project.tale.strip() not in ("Não aplicável.", "Não aplicável"):
        document.add_page_break()
        _add_text_block(document, "TALE — Termo para Responsáveis de Menores", project.tale)

    if project.assent_term and project.assent_term.strip() not in ("Não aplicável.", "Não aplicável"):
        document.add_page_break()
        _add_text_block(document, "Termo de Assentimento", project.assent_term)

    document.add_page_break()
    _add_text_block(document, "Carta de Anuência Institucional", project.institution_letter or "")

    document.save(filename)
    return filename
