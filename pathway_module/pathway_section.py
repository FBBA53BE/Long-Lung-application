"""
pathway_section.py
───────────────────
ส่วนที่เพิ่มเข้าไปใน app.py เดิม
ใส่ต่อจาก classification result block

วิธีใช้:
  from pathway_section import render_pathway_section
  render_pathway_section(cancer_type)
"""

import streamlit as st
import pandas as pd
import io
import sys
import os

sys.path.append(os.path.dirname(__file__))
from oncokb_client import query_all_mutations, LEVEL_LABELS, LEVEL_COLORS
from pathway_viewer import generate_pathway_html

# ─── ตัวอย่าง preset mutations ต่อ cancer type ───────────────────────────────
PRESETS = {
    "Adenocarcinoma": [
        {"gene": "EGFR",  "alteration": "L858R",        "vaf": 0.42},
        {"gene": "TP53",  "alteration": "R248W",         "vaf": 0.38},
        {"gene": "MET",   "alteration": "Amplification", "vaf": "HIGH"},
    ],
    "Squamous Cell Carcinoma": [
        {"gene": "TP53",  "alteration": "R175H",         "vaf": 0.55},
        {"gene": "KRAS",  "alteration": "G12C",           "vaf": 0.28},
    ],
    "Large Cell Carcinoma": [
        {"gene": "KRAS",  "alteration": "G12C",           "vaf": 0.35},
        {"gene": "TP53",  "alteration": "V157F",          "vaf": 0.41},
        {"gene": "BRAF",  "alteration": "V600E",          "vaf": 0.22},
    ],
    "Benign": [],
}

EXPECTED_COLS = {"gene", "alteration", "vaf"}  # columns ที่ต้องมีใน CSV


def _parse_csv(uploaded_file) -> list[dict] | None:
    """Parse CSV → mutation list, คืน None ถ้า format ไม่ถูก"""
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [c.strip().lower() for c in df.columns]
        missing = EXPECTED_COLS - set(df.columns)
        if missing:
            st.error(f"CSV ต้องมีคอลัมน์: {', '.join(EXPECTED_COLS)} — ขาด: {', '.join(missing)}")
            return None
        mutations = []
        for _, row in df.iterrows():
            mutations.append({
                "gene":       str(row["gene"]).strip().upper(),
                "alteration": str(row["alteration"]).strip(),
                "vaf":        row["vaf"],
            })
        return mutations
    except Exception as e:
        st.error(f"อ่าน CSV ไม่ได้: {e}")
        return None


def _build_patient_info(patient_name: str, cancer_type: str, stage: str,
                         tmb: str, pdl1: str) -> dict:
    badges = [
        {"text": cancer_type, "cls": "badge-blue"},
    ]
    if tmb:
        badges.append({"text": f"TMB: {tmb}", "cls": "badge-amber"})
    if pdl1:
        badges.append({"text": f"PD-L1: {pdl1}%", "cls": "badge-amber"})

    return {
        "name":     patient_name or "Unknown Patient",
        "subtitle": f"Stage {stage} NSCLC" if stage else cancer_type,
        "badges":   badges,
    }


def render_pathway_section(cancer_type: str = "Adenocarcinoma"):
    """
    เรียกฟังก์ชันนี้ใน app.py ต่อจาก classification block
    """
    st.divider()

    # ─── Header ──────────────────────────────────────────────────────────────
    st.markdown("### Pathway & Drug Recommendation")
    st.caption(
        "ป้อนข้อมูล mutation จาก NGS report ของผู้ป่วย "
        "เพื่อดู pathway ที่ได้รับผลกระทบและยาที่แนะนำ"
    )

    # ─── Patient info ─────────────────────────────────────────────────────────
    with st.expander("Patient info (optional)", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            patient_name = st.text_input("Patient ID / Name", value="Patient #001")
        with c2:
            stage = st.selectbox("Stage", ["I", "II", "IIIA", "IIIB", "IV", "Unknown"])
        with c3:
            tmb = st.text_input("TMB (mut/Mb)", value="8")
        with c4:
            pdl1 = st.text_input("PD-L1 (%)", value="")

    # ─── Mutation input ───────────────────────────────────────────────────────
    st.markdown("#### Mutation input")
    input_mode = st.radio(
        "เลือกวิธีป้อนข้อมูล",
        ["Upload NGS CSV", "ใช้ preset ตาม cancer type", "ป้อนเอง"],
        horizontal=True,
    )

    mutations = []

    if input_mode == "Upload NGS CSV":
        st.markdown(
            "**Format CSV:** ต้องมีคอลัมน์ `gene`, `alteration`, `vaf`\n\n"
            "```\ngene,alteration,vaf\nEGFR,L858R,0.42\nTP53,R248W,0.38\n```"
        )
        uploaded = st.file_uploader(
            "Upload NGS result (.csv)",
            type=["csv"],
            help="ผลจาก NGS lab เช่น FoundationOne, Guardant360",
        )
        if uploaded:
            parsed = _parse_csv(uploaded)
            if parsed:
                mutations = parsed
                st.success(f"โหลด {len(mutations)} mutations จาก CSV")

    elif input_mode == "ใช้ preset ตาม cancer type":
        preset_type = st.selectbox(
            "Cancer type",
            list(PRESETS.keys()),
            index=list(PRESETS.keys()).index(cancer_type)
            if cancer_type in PRESETS else 0,
        )
        mutations = PRESETS[preset_type]
        if mutations:
            st.info(
                f"Preset: {len(mutations)} mutations สำหรับ {preset_type} "
                f"({', '.join(m['gene']+' '+m['alteration'] for m in mutations)})"
            )
        else:
            st.info("Benign — ไม่มี driver mutation ที่ต้องรักษาด้วย targeted therapy")

    else:  # Manual
        st.markdown("เพิ่ม mutation ทีละตัว:")
        n = st.number_input("จำนวน mutations", min_value=1, max_value=10, value=2)
        for i in range(int(n)):
            cc1, cc2, cc3 = st.columns([2, 2, 1])
            with cc1:
                g = st.text_input(f"Gene {i+1}", key=f"gene_{i}",
                                   placeholder="เช่น EGFR")
            with cc2:
                a = st.text_input(f"Alteration {i+1}", key=f"alt_{i}",
                                   placeholder="เช่น L858R")
            with cc3:
                v = st.text_input(f"VAF {i+1}", key=f"vaf_{i}",
                                   placeholder="0.42")
            if g and a:
                mutations.append({
                    "gene": g.strip().upper(),
                    "alteration": a.strip(),
                    "vaf": v.strip() if v else "",
                })

    # ─── Analyze button ────────────────────────────────────────────────────────
    if mutations and st.button("Analyze Pathway & Get Drug Recommendation", type="primary"):
        with st.spinner("กำลัง query OncoKB และสร้าง pathway graph..."):
            # Query OncoKB
            enriched = query_all_mutations(mutations)
            st.session_state["enriched_mutations"] = enriched

            # Build patient info
            patient_info = _build_patient_info(
                patient_name=locals().get("patient_name", "Patient"),
                cancer_type=cancer_type,
                stage=locals().get("stage", "Unknown"),
                tmb=locals().get("tmb", ""),
                pdl1=locals().get("pdl1", ""),
            )
            st.session_state["patient_info"] = patient_info

        st.success("Done!")

    # ─── Show results ─────────────────────────────────────────────────────────
    if "enriched_mutations" in st.session_state:
        enriched  = st.session_state["enriched_mutations"]
        pt_info   = st.session_state.get("patient_info", {})

        # Drug summary table (เหนือ graph)
        _render_drug_table(enriched)

        # Pathway graph
        st.markdown("#### Pathway viewer")
        st.caption("กดยาด้านบนกราฟเพื่อดู mechanism — กดที่ node (สีแดง) เพื่อดูรายละเอียด mutation")
        html = generate_pathway_html(enriched, pt_info)
        st.components.v1.html(html, height=700, scrolling=False)

        # Raw data download
        with st.expander("Raw OncoKB data"):
            for m in enriched:
                st.json({
                    "gene":       m["gene"],
                    "alteration": m["alteration"],
                    "oncokb":     m["oncokb"],
                })

    
def _render_drug_table(enriched: list[dict]):
    """แสดง drug recommendation table แบบ clean"""
    st.markdown("#### Drug recommendations from OncoKB")
    rows = []
    for m in enriched:
        for tx in m["oncokb"].get("treatments", []):
            drug_str = " + ".join(d["drugName"] for d in tx.get("drugs", []))
            level    = tx.get("level", "")
            rows.append({
                "Gene":           m["gene"] + " " + m.get("alteration",""),
                "Drug(s)":        drug_str,
                "Evidence Level": level,
                "Level label":    LEVEL_LABELS.get(level, level),
                "Indication":     ", ".join(tx.get("approvedIndications", [])),
            })

    if rows:
        df = pd.DataFrame(rows)

        def color_level(val):
            colors = {
                "LEVEL_1":  "background-color:#eaf3de;color:#27500a",
                "LEVEL_2":  "background-color:#e6f1fb;color:#0c447c",
                "LEVEL_3A": "background-color:#faeeda;color:#633806",
                "LEVEL_3B": "background-color:#faeeda;color:#633806",
                "LEVEL_4":  "background-color:#f1efe8;color:#5f5e5a",
            }
            return colors.get(val, "")

        styled = df.style.map(color_level, subset=["Evidence Level"])
        st.dataframe(styled, use_container_width=True, hide_index=True)
    else:
        st.info("ไม่พบ approved drug สำหรับ mutation เหล่านี้ใน OncoKB — อาจต้องดู clinical trials")


# ─── ตัวอย่าง CSV สำหรับ download ────────────────────────────────────────────
SAMPLE_CSV = """gene,alteration,vaf
EGFR,L858R,0.42
TP53,R248W,0.38
MET,Amplification,HIGH
"""

def get_sample_csv_bytes() -> bytes:
    return SAMPLE_CSV.encode("utf-8")
