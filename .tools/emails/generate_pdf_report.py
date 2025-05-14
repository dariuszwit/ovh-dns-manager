from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
import os
import pandas as pd


def generate_pdf_report(txt_summary, graph_image, chart_accounts, chart_forwardings, output_pdf, notes_file=None):
    """Generuje końcowy raport PDF z tabelą kont, grafiką i dwoma wykresami (konta + przekierowania)."""

    # Czcionka z obsługą polskich znaków
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
    if not os.path.exists(font_path):
        raise FileNotFoundError("Brakuje czcionki DejaVuSans.ttf w katalogu 'fonts'!")

    pdfmetrics.registerFont(TTFont('DejaVu', font_path))

    width, height = A4
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()
    for style in styles.byName:
        styles[style].fontName = 'DejaVu'

    story = []

    # -------------------- Tytuł --------------------
    story.append(Paragraph("Końcowy Raport: Konta Email i Pakiety", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Wygenerowano za pomocą OVH API Manager", styles["Normal"]))
    story.append(Paragraph(f"Plik źródłowy: {os.path.basename(txt_summary)}", styles["Normal"]))
    story.append(Spacer(1, 24))

    # -------------------- Sekcja 1: Tabela kont --------------------
    story.append(Paragraph("Sekcja 1: Podsumowanie kont i pakietów", styles["Heading2"]))
    story.append(Paragraph("Poniżej znajdują się konta email oraz przypisane pakiety.", styles["Normal"]))
    story.append(Spacer(1, 12))

    csv_path = txt_summary.replace(".txt", ".csv")
    if not os.path.exists(csv_path):
        story.append(Paragraph("❌ Brak pliku CSV z danymi kont email.", styles["Normal"]))
    else:
        try:
            df = pd.read_csv(csv_path)
            if 'service' in df.columns and 'email' in df.columns and 'offer' in df.columns:
                table_data = [["Serwis", "Email", "Pakiet"]]
                for _, row in df.iterrows():
                    table_data.append([row["service"], row["email"], row["offer"]])

                table = Table(table_data, colWidths=[6 * cm, 7 * cm, 4 * cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'DejaVu'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.gray),
                ]))
                story.append(table)
            else:
                story.append(Paragraph("❌ Plik CSV nie zawiera wymaganych kolumn: service, email, offer.", styles["Normal"]))
        except Exception as e:
            story.append(Paragraph(f"❌ Błąd przy odczycie pliku CSV: {e}", styles["Normal"]))

    story.append(Spacer(1, 24))

    # -------------------- Sekcja 2: Notatki --------------------
    if notes_file and os.path.exists(notes_file):
        story.append(Paragraph("Sekcja 2: Uwagi i notatki", styles["Heading2"]))
        story.append(Spacer(1, 6))
        with open(notes_file, 'r', encoding='utf-8') as nf:
            for line in nf:
                story.append(Paragraph(line.strip(), styles["Normal"]))
        story.append(Spacer(1, 24))

    # -------------------- Sekcja 3: Graf kont i przekierowań --------------------
    if graph_image and os.path.exists(graph_image):
        story.append(Paragraph("Sekcja 3: Graf kont i przekierowań", styles["Heading2"]))
        story.append(Paragraph("Graf przedstawia powiązania między kontami, przekierowaniami i DMARC.", styles["Normal"]))
        story.append(Spacer(1, 12))
        story.append(Image(graph_image, width=width - 4 * cm, height=10 * cm))

    # -------------------- Sekcja 4: Wykres kont --------------------
    if chart_accounts and os.path.exists(chart_accounts):
        story.append(Paragraph("Sekcja 4: Wykres liczby kont email", styles["Heading2"]))
        story.append(Paragraph("Wykres przedstawia liczbę kont przypisanych do serwisów.", styles["Normal"]))
        story.append(Spacer(1, 12))
        story.append(Image(chart_accounts, width=width - 4 * cm, height=10 * cm))

    # -------------------- Sekcja 5: Wykres przekierowań --------------------
    if chart_forwardings and os.path.exists(chart_forwardings):
        story.append(Paragraph("Sekcja 5: Wykres liczby przekierowań", styles["Heading2"]))
        story.append(Paragraph("Wykres przedstawia liczbę aliasów/przekierowań w poszczególnych serwisach.", styles["Normal"]))
        story.append(Spacer(1, 12))
        story.append(Image(chart_forwardings, width=width - 4 * cm, height=10 * cm))

    doc.build(story)
    print(f"✅ Końcowy raport PDF zapisany do: {output_pdf}")
