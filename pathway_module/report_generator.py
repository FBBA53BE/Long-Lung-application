"""
report_generator.py
────────────────────
สร้าง PDF report สรุปผลการวิเคราะห์ CT scan + mutation + drug recommendation
ใช้ใน app.py:
    from pathway_module.report_generator import generate_report_pdf
    pdf_bytes = generate_report_pdf(report_data)
    st.download_button("Download Report", pdf_bytes, "report.pdf", "application/pdf")
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── Color palette ─────────────────────────────────────────────────────────────
C_BG       = colors.HexColor("#050A0E")
C_ACCENT   = colors.HexColor("#00C8A0")
C_ACCENT2  = colors.HexColor("#0077FF")
C_DANGER   = colors.HexColor("#FF4D6D")
C_WARN     = colors.HexColor("#FFB347")
C_MUTED    = colors.HexColor("#5A7A70")
C_SURFACE  = colors.HexColor("#112030")
C_TEXT     = colors.HexColor("#1a1a1a")
C_WHITE    = colors.white

LEVEL_COLORS = {
    "LEVEL_1":  colors.HexColor("#27500A"),
    "LEVEL_2":  colors.HexColor("#0C447C"),
    "LEVEL_3A": colors.HexColor("#633806"),
    "LEVEL_3B": colors.HexColor("#633806"),
    "LEVEL_4":  colors.HexColor("#5F5E5A"),
    "LEVEL_R1": colors.HexColor("#791F1F"),
}
LEVEL_BG = {
    "LEVEL_1":  colors.HexColor("#EAF3DE"),
    "LEVEL_2":  colors.HexColor("#E6F1FB"),
    "LEVEL_3A": colors.HexColor("#FAEEDA"),
    "LEVEL_3B": colors.HexColor("#FAEEDA"),
    "LEVEL_4":  colors.HexColor("#F1EFE8"),
    "LEVEL_R1": colors.HexColor("#FCEBEB"),
}
LEVEL_LABELS = {
    "LEVEL_1":  "FDA Approved",
    "LEVEL_2":  "Standard of Care",
    "LEVEL_3A": "Clinical Evidence",
    "LEVEL_3B": "Clinical Evidence",
    "LEVEL_4":  "Biological Evidence",
    "LEVEL_R1": "Resistance",
}

# ── Styles ────────────────────────────────────────────────────────────────────
def _make_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles["title"] = ParagraphStyle(
        "title", fontSize=22, fontName="Helvetica-Bold",
        textColor=C_TEXT, spaceAfter=4, leading=26,
    )
    styles["subtitle"] = ParagraphStyle(
        "subtitle", fontSize=11, fontName="Helvetica",
        textColor=C_MUTED, spaceAfter=2,
    )
    styles["section"] = ParagraphStyle(
        "section", fontSize=10, fontName="Helvetica-Bold",
        textColor=C_ACCENT, spaceBefore=14, spaceAfter=6,
        borderPad=4,
    )
    styles["body"] = ParagraphStyle(
        "body", fontSize=9, fontName="Helvetica",
        textColor=C_TEXT, spaceAfter=3, leading=13,
    )
    styles["body_bold"] = ParagraphStyle(
        "body_bold", fontSize=9, fontName="Helvetica-Bold",
        textColor=C_TEXT, spaceAfter=3,
    )
    styles["small"] = ParagraphStyle(
        "small", fontSize=8, fontName="Helvetica",
        textColor=C_MUTED, spaceAfter=2,
    )
    styles["drug_name"] = ParagraphStyle(
        "drug_name", fontSize=10, fontName="Helvetica-Bold",
        textColor=C_TEXT, spaceAfter=2,
    )
    styles["center"] = ParagraphStyle(
        "center", fontSize=9, fontName="Helvetica",
        textColor=C_MUTED, alignment=TA_CENTER,
    )
    return styles


# ── Header / Footer ───────────────────────────────────────────────────────────
def _on_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    # Header bar
    canvas.setFillColor(C_BG)
    canvas.rect(0, h - 1.2*cm, w, 1.2*cm, fill=1, stroke=0)
    canvas.setFillColor(C_ACCENT)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(1.5*cm, h - 0.85*cm, "Long Lung — AI-Powered Pulmonary Analysis")
    canvas.setFillColor(C_MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - 1.5*cm, h - 0.85*cm,
                           datetime.now().strftime("%d %b %Y"))
    # Footer
    canvas.setFillColor(C_MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawCentredString(w/2, 0.7*cm,
        "This report is generated for clinical reference only — not a substitute for professional medical judgment.")
    canvas.drawRightString(w - 1.5*cm, 0.7*cm, f"Page {doc.page}")
    # Accent line
    canvas.setStrokeColor(C_ACCENT)
    canvas.setLineWidth(1.5)
    canvas.line(0, h - 1.2*cm, w, h - 1.2*cm)
    canvas.restoreState()


# ── Section divider ───────────────────────────────────────────────────────────
def _section_header(title, styles):
    return [
        Spacer(1, 0.3*cm),
        Paragraph(title.upper(), styles["section"]),
        HRFlowable(width="100%", thickness=0.5,
                   color=C_ACCENT, spaceAfter=6),
    ]


# ── Patient info table ────────────────────────────────────────────────────────
def _patient_table(patient_info: dict, pred_class: str,
                   confidence: float, styles):
    data = [
        ["Patient", patient_info.get("name", "—"),
         "Cancer type", pred_class],
        ["Stage",   patient_info.get("stage", "—"),
         "Confidence", f"{confidence:.1f}%"],
        ["TMB",     patient_info.get("tmb", "—"),
         "PD-L1",   patient_info.get("pdl1", "—")],
        ["Date",    datetime.now().strftime("%d %b %Y"), "", ""],
    ]
    col_w = [2.5*cm, 5.5*cm, 2.5*cm, 5.5*cm]
    t = Table(data, colWidths=col_w)
    t.setStyle(TableStyle([
        ("FONTNAME",  (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",  (0,0), (-1,-1), 9),
        ("FONTNAME",  (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",  (2,0), (2,-1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0,0), (0,-1), C_MUTED),
        ("TEXTCOLOR", (2,0), (2,-1), C_MUTED),
        ("BACKGROUND",(0,0), (-1,-1), colors.HexColor("#F8F8F6")),
        ("ROWBACKGROUNDS", (0,0), (-1,-1),
         [colors.white, colors.HexColor("#F8F8F6")]),
        ("GRID",      (0,0), (-1,-1), 0.3, colors.HexColor("#E0E0DC")),
        ("ROUNDEDCORNERS", [4]),
        ("TOPPADDING",(0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",(0,0), (-1,-1), 8),
    ]))
    return t


# ── Classification result ─────────────────────────────────────────────────────
def _classification_section(pred_class: str, confidence: float,
                             probs: dict, styles):
    elems = _section_header("Classification Result", styles)

    is_cancer = pred_class not in ["Normal", "Benign"]
    color = C_DANGER if is_cancer else C_ACCENT

    # Result badge
    badge_data = [[
        Paragraph(f"{'⚠ ' if is_cancer else '✓ '}{pred_class}",
                  ParagraphStyle("badge", fontSize=14,
                                 fontName="Helvetica-Bold",
                                 textColor=color)),
        Paragraph(f"Confidence: {confidence:.1f}%",
                  ParagraphStyle("conf", fontSize=10,
                                 fontName="Helvetica",
                                 textColor=C_MUTED,
                                 alignment=TA_RIGHT)),
    ]]
    badge = Table(badge_data, colWidths=[10*cm, 6*cm])
    badge.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F8F8F6")),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("LINEBELOW", (0,0), (-1,0), 2, color),
    ]))
    elems.append(badge)
    elems.append(Spacer(1, 0.3*cm))

    # Probability bars as table
    if probs:
        bar_data = [["Class", "Probability", "Bar"]]
        sorted_probs = sorted(probs.items(), key=lambda x: -x[1])
        for cls, prob in sorted_probs:
            pct = f"{prob*100:.1f}%"
            bar_len = max(1, int(prob * 80))
            bar = "█" * bar_len
            bar_data.append([cls, pct, bar])

        bar_t = Table(bar_data, colWidths=[6*cm, 2.5*cm, 7.5*cm])
        bar_t.setStyle(TableStyle([
            ("FONTNAME",  (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTNAME",  (0,1), (-1,-1), "Helvetica"),
            ("FONTSIZE",  (0,0), (-1,-1), 8),
            ("TEXTCOLOR", (0,0), (-1,0),  C_MUTED),
            ("TEXTCOLOR", (2,1), (2,-1),  C_ACCENT),
            ("GRID",      (0,0), (-1,-1), 0.3,
             colors.HexColor("#E0E0DC")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1),
             [colors.white, colors.HexColor("#F8F8F6")]),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ]))
        elems.append(bar_t)
    return elems


# ── Mutation section ──────────────────────────────────────────────────────────
def _mutation_section(enriched_mutations: list, styles):
    elems = _section_header(
        f"Mutations Detected ({len(enriched_mutations)})", styles)

    mut_data = [["Gene", "Alteration", "VAF", "Oncogenicity", "Effect"]]
    for m in enriched_mutations:
        oncokb  = m.get("oncokb", {})
        vaf_raw = m.get("vaf", "")
        try:
            vaf_str = f"{float(vaf_raw)*100:.1f}%" \
                if float(str(vaf_raw).replace("%","")) <= 1 \
                else f"{float(str(vaf_raw).replace('%','')):.1f}%"
        except Exception:
            vaf_str = str(vaf_raw)

        mut_data.append([
            m.get("gene", ""),
            m.get("alteration", ""),
            vaf_str,
            oncokb.get("oncogenicity", "Unknown"),
            oncokb.get("mutationEffect", "Unknown"),
        ])

    col_w = [2.5*cm, 3*cm, 1.8*cm, 3.2*cm, 5.5*cm]
    t = Table(mut_data, colWidths=col_w)
    style = [
        ("FONTNAME",  (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTNAME",  (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",  (0,0), (-1,-1), 8),
        ("BACKGROUND",(0,0), (-1,0),  C_BG),
        ("TEXTCOLOR", (0,0), (-1,0),  C_WHITE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.white, colors.HexColor("#F8F8F6")]),
        ("GRID",      (0,0), (-1,-1), 0.3,
         colors.HexColor("#E0E0DC")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("ALIGN",     (2,0), (2,-1), "CENTER"),
    ]
    # สีแดง oncogenic
    for i, m in enumerate(enriched_mutations, 1):
        if "Oncogenic" in m.get("oncokb",{}).get("oncogenicity",""):
            style.append(("TEXTCOLOR", (3,i), (3,i), C_DANGER))
    t.setStyle(TableStyle(style))
    elems.append(t)
    return elems


# ── Drug recommendation section ───────────────────────────────────────────────
def _drug_section(enriched_mutations: list, styles):
    elems = _section_header("Drug Recommendations", styles)

    # รวม drugs จากทุก mutation
    all_drugs = []
    seen = set()
    for m in enriched_mutations:
        for tx in m.get("oncokb", {}).get("treatments", []):
            drug_str = " + ".join(d["drugName"] for d in tx.get("drugs", []))
            if drug_str in seen:
                continue
            seen.add(drug_str)
            all_drugs.append({
                "drug":  drug_str,
                "gene":  m["gene"],
                "level": tx.get("level", "LEVEL_4"),
                "indications": ", ".join(tx.get("approvedIndications", [])),
            })

    if not all_drugs:
        elems.append(Paragraph(
            "No approved drug interactions found in current database. "
            "Consider querying OncoKB API with academic token for comprehensive results.",
            styles["body"]))
        return elems

    # เรียงตาม level
    level_order = {"LEVEL_1":0,"LEVEL_2":1,"LEVEL_3A":2,
                   "LEVEL_3B":3,"LEVEL_4":4,"LEVEL_R1":5}
    all_drugs.sort(key=lambda x: level_order.get(x["level"], 9))

    drug_data = [["Drug(s)", "Target Gene", "Evidence Level", "Indication"]]
    for d in all_drugs:
        drug_data.append([
            d["drug"],
            d["gene"],
            LEVEL_LABELS.get(d["level"], d["level"]),
            d["indications"] or "NSCLC",
        ])

    col_w = [5.5*cm, 2.5*cm, 3.5*cm, 4.5*cm]
    t = Table(drug_data, colWidths=col_w)
    style = [
        ("FONTNAME",  (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTNAME",  (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",  (0,0), (-1,-1), 8),
        ("BACKGROUND",(0,0), (-1,0),  C_BG),
        ("TEXTCOLOR", (0,0), (-1,0),  C_WHITE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.white, colors.HexColor("#F8F8F6")]),
        ("GRID",      (0,0), (-1,-1), 0.3,
         colors.HexColor("#E0E0DC")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ]
    # สีตาม level
    for i, d in enumerate(all_drugs, 1):
        lvl = d["level"]
        bg  = LEVEL_BG.get(lvl,  colors.HexColor("#F1EFE8"))
        fg  = LEVEL_COLORS.get(lvl, C_MUTED)
        style.append(("BACKGROUND", (2,i), (2,i), bg))
        style.append(("TEXTCOLOR",  (2,i), (2,i), fg))
        style.append(("FONTNAME",   (2,i), (2,i), "Helvetica-Bold"))
    t.setStyle(TableStyle(style))
    elems.append(t)
    return elems


# ── Pathway diagram (static ASCII-style) ─────────────────────────────────────
def _pathway_section(enriched_mutations: list, styles):
    elems = _section_header("Pathway Overview", styles)

    mutated = {m["gene"].upper() for m in enriched_mutations}

    elems.append(Paragraph(
        "Nodes highlighted in red indicate mutated genes detected in this patient. "
        "Arrows show signal flow through key oncogenic pathways.",
        styles["small"]))
    elems.append(Spacer(1, 0.2*cm))

    # pathway summary table
    pathway_rows = [
        ["Pathway", "Key Nodes", "Mutated in Patient", "Clinical Implication"],
        ["MAPK/ERK", "EGFR → RAS → RAF → MEK → ERK",
         ", ".join(g for g in ["EGFR","KRAS","BRAF","MAP2K1","MAP2K2","NF1"] if g in mutated) or "—",
         "Drives proliferation — EGFR/BRAF/MEK inhibitors"],
        ["PI3K/AKT", "EGFR → PI3K → AKT → mTOR",
         ", ".join(g for g in ["PIK3CA","AKT1","MTOR","PTEN","PIK3R1"] if g in mutated) or "—",
         "Drives survival — PI3K/AKT/mTOR inhibitors"],
        ["TP53/MDM2", "TP53 → Apoptosis (MDM2 degrades TP53)",
         ", ".join(g for g in ["TP53","MDM2"] if g in mutated) or "—",
         "Tumor suppressor loss — affects chemo response"],
        ["Immune", "PD-L1/PD-1 checkpoint",
         ", ".join(g for g in ["CD274","PDCD1"] if g in mutated) or "—",
         "Immune evasion — checkpoint inhibitors"],
        ["RTK fusion", "ALK / ROS1 / RET / NTRK fusions",
         ", ".join(g for g in ["ALK","ROS1","RET","NTRK1","NTRK2","NTRK3"] if g in mutated) or "—",
         "Fusion-driven — TKI highly effective"],
        ["DNA repair", "BRCA1/2, ATM, POLE",
         ", ".join(g for g in ["BRCA1","BRCA2","ATM","POLE"] if g in mutated) or "—",
         "HRD — PARP inhibitors, immunotherapy"],
    ]

    col_w = [3.2*cm, 5*cm, 3.5*cm, 4.3*cm]
    t = Table(pathway_rows, colWidths=col_w)
    style = [
        ("FONTNAME",  (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTNAME",  (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",  (0,0), (-1,-1), 7.5),
        ("BACKGROUND",(0,0), (-1,0),  C_BG),
        ("TEXTCOLOR", (0,0), (-1,0),  C_WHITE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.white, colors.HexColor("#F8F8F6")]),
        ("GRID",      (0,0), (-1,-1), 0.3,
         colors.HexColor("#E0E0DC")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
        ("VALIGN",    (0,0), (-1,-1), "TOP"),
        ("WORDWRAP",  (0,0), (-1,-1), True),
    ]
    # highlight rows ที่ mutated
    for i, row in enumerate(pathway_rows[1:], 1):
        if row[2] != "—":
            style.append(("TEXTCOLOR", (2,i), (2,i), C_DANGER))
            style.append(("FONTNAME",  (2,i), (2,i), "Helvetica-Bold"))
    t.setStyle(TableStyle(style))
    elems.append(t)
    return elems


# ── Imaging section ───────────────────────────────────────────────────────────
def _imaging_section(ct_img_bytes=None, heatmap_bytes=None,
                     seg_bytes=None, styles=None):
    elems = _section_header("CT Imaging Analysis", styles)

    images = []
    if ct_img_bytes:
        images.append(("CT Scan Input", ct_img_bytes))
    if heatmap_bytes:
        images.append(("Grad-CAM Heatmap", heatmap_bytes))
    if seg_bytes:
        images.append(("Tumor Segmentation", seg_bytes))

    if not images:
        elems.append(Paragraph("No imaging data available.", styles["small"]))
        return elems

    img_data = []
    for label, img_bytes in images:
        try:
            img = RLImage(io.BytesIO(img_bytes), width=5*cm, height=5*cm)
            img_data.append([img, Paragraph(label, styles["center"])])
        except Exception:
            pass

    if img_data:
        # วาง images เป็น row
        row_imgs  = [d[0] for d in img_data]
        row_labels = [d[1] for d in img_data]
        n = len(row_imgs)
        col_w = [16*cm / n] * n

        t_imgs   = Table([row_imgs],  colWidths=col_w)
        t_labels = Table([row_labels], colWidths=col_w)
        for t in [t_imgs, t_labels]:
            t.setStyle(TableStyle([
                ("ALIGN",  (0,0), (-1,-1), "CENTER"),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ]))
        elems.append(t_imgs)
        elems.append(Spacer(1, 0.15*cm))
        elems.append(t_labels)

    return elems


# ── Disclaimer ────────────────────────────────────────────────────────────────
def _disclaimer(styles):
    return [
        Spacer(1, 0.5*cm),
        HRFlowable(width="100%", thickness=0.3, color=C_MUTED),
        Spacer(1, 0.2*cm),
        Paragraph(
            "<b>Disclaimer:</b> This report is generated by an AI-assisted system "
            "(Long Lung) using EfficientNet-B0 classification and U-Net segmentation. "
            "Drug recommendations are sourced from OncoKB / DGIdb knowledge bases. "
            "All findings must be reviewed and confirmed by a qualified clinician. "
            "This report does not constitute medical advice or a diagnosis.",
            ParagraphStyle("disc", fontSize=7, fontName="Helvetica",
                           textColor=C_MUTED, leading=10)),
    ]


# ── Main entry point ──────────────────────────────────────────────────────────
def generate_report_pdf(
    patient_info: dict,
    pred_class: str,
    confidence: float,
    probs: dict,
    enriched_mutations: list,
    ct_img_bytes: bytes = None,
    heatmap_bytes: bytes = None,
    seg_bytes: bytes = None,
) -> bytes:
    """
    Parameters
    ──────────
    patient_info        : {"name","stage","tmb","pdl1"}
    pred_class          : "Adenocarcinoma" etc.
    confidence          : 0-100 float
    probs               : {"Adenocarcinoma": 0.99, ...}
    enriched_mutations  : list จาก query_all_mutations()
    ct_img_bytes        : PNG/JPG bytes ของ CT scan (optional)
    heatmap_bytes       : PNG bytes ของ Grad-CAM (optional)
    seg_bytes           : PNG bytes ของ segmentation (optional)

    Returns
    ───────
    bytes ของ PDF
    """
    buf    = io.BytesIO()
    styles = _make_styles()

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2*cm,    bottomMargin=1.5*cm,
    )

    story = []

    # ── Cover info ────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Lung Cancer Analysis Report", styles["title"]))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}",
        styles["subtitle"]))
    story.append(Spacer(1, 0.3*cm))

    # Patient info table
    story.extend(_section_header("Patient Information", styles))
    story.append(_patient_table(patient_info, pred_class, confidence, styles))

    # Classification
    story.extend(_classification_section(pred_class, confidence, probs, styles))

    # Imaging (CT, heatmap, segmentation)
    story.extend(_imaging_section(ct_img_bytes, heatmap_bytes, seg_bytes, styles))

    # Mutations
    if enriched_mutations:
        story.extend(_mutation_section(enriched_mutations, styles))

    # Pathway overview
    if enriched_mutations:
        story.extend(_pathway_section(enriched_mutations, styles))

    # Drug recommendations
    if enriched_mutations:
        story.extend(_drug_section(enriched_mutations, styles))

    # Disclaimer
    story.extend(_disclaimer(styles))

    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    return buf.getvalue()
