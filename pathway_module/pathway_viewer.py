"""
pathway_viewer.py
─────────────────
Generate Cytoscape.js interactive pathway HTML
รับ mutation data → คืน HTML string พร้อม inject ลง Streamlit
"""

import json


# ─── Core pathway graph (static biology) ──────────────────────────────────────
PATHWAY_NODES = [
    # (id, label, type, x_hint, y_hint)
    ("EGFR",         "EGFR",          "receptor",   "receptor"),
    ("MET",          "MET",           "receptor",   "receptor"),
    ("ALK",          "ALK",           "receptor",   "receptor"),
    ("RAS",          "RAS",           "signaling",  "mapk"),
    ("RAF",          "RAF",           "signaling",  "mapk"),
    ("MEK",          "MEK",           "signaling",  "mapk"),
    ("ERK",          "ERK",           "signaling",  "mapk"),
    ("PI3K",         "PI3K",          "signaling",  "pi3k"),
    ("AKT",          "AKT",           "signaling",  "pi3k"),
    ("mTOR",         "mTOR",          "signaling",  "pi3k"),
    ("MDM2",         "MDM2",          "signaling",  "tp53"),
    ("TP53",         "TP53",          "suppressor", "tp53"),
    ("STAT3",        "STAT3",         "signaling",  "jak"),
    ("JAK",          "JAK",           "signaling",  "jak"),
    ("T-cell",       "T-cell\n(immune)", "immune",  "immune"),
    ("Proliferation","Proliferation", "outcome",    "outcome"),
    ("Cell survival","Cell Survival", "outcome",    "outcome"),
    ("Apoptosis",    "Apoptosis\n(suppr.)", "outcome", "outcome"),
    ("ROS1",  "ROS1",  "receptor", "receptor"),
    ("RET",   "RET",   "receptor", "receptor"),
    ("FGFR",  "FGFR",  "receptor", "receptor"),
    ("NTRK",  "NTRK",  "receptor", "receptor"),
]

PATHWAY_EDGES = [
    ("EGFR",  "RAS",          "activates"),
    ("EGFR",  "PI3K",         "activates"),
    ("EGFR",  "JAK",          "activates"),
    ("MET",   "RAS",          "activates"),
    ("MET",   "PI3K",         "activates"),
    ("ALK",   "RAS",          "activates"),
    ("ALK",   "PI3K",         "activates"),
    ("RAS",   "RAF",          "activates"),
    ("RAF",   "MEK",          "activates"),
    ("MEK",   "ERK",          "activates"),
    ("ERK",   "Proliferation","activates"),
    ("PI3K",  "AKT",          "activates"),
    ("AKT",   "mTOR",         "activates"),
    ("AKT",   "MDM2",         "phosphorylates"),
    ("AKT",   "Cell survival","activates"),
    ("mTOR",  "Proliferation","activates"),
    ("mTOR",  "Cell survival","activates"),
    ("MDM2",  "TP53",         "degrades"),
    ("TP53",  "Apoptosis",    "induces"),
    ("JAK",   "STAT3",        "activates"),
    ("STAT3", "Proliferation","activates"),
    ("T-cell","Apoptosis",    "immune kill"),
    ("ROS1", "RAS", "activates"),
    ("RET",  "RAS", "activates"),
    ("FGFR", "PI3K","activates"),
    ("NTRK", "RAS", "activates"),
]

# ─── Drug → pathway effect mapping ────────────────────────────────────────────
DRUG_EFFECTS = {
 
    # ── EGFR inhibitors ──────────────────────────────────────
    "Osimertinib": {
        "color": "#378ADD", "targets": ["EGFR"],
        "cascade": ["RAS","PI3K","RAF","AKT","MEK","mTOR"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "3rd-gen EGFR TKI — covalently binds L858R & T790M mutant EGFR",
        "cascade_text": ["EGFR kinase blocked","→ RAS cannot activate","→ RAF/MEK/ERK suppressed","→ PI3K/AKT/mTOR suppressed","→ Proliferation + Survival reduced"],
    },
    "Erlotinib": {
        "color": "#185FA5", "targets": ["EGFR"],
        "cascade": ["RAS","PI3K","RAF","AKT","MEK"],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "1st-gen EGFR TKI — reversible competitive inhibitor",
        "cascade_text": ["EGFR blocked (reversible)","→ RAS/RAF/MEK suppressed","→ PI3K/AKT suppressed","→ Proliferation reduced"],
    },
    "Gefitinib": {
        "color": "#185FA5", "targets": ["EGFR"],
        "cascade": ["RAS","PI3K","RAF","AKT","MEK"],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "1st-gen EGFR TKI — competitive ATP binding inhibitor",
        "cascade_text": ["EGFR blocked","→ RAS/RAF/MEK suppressed","→ Proliferation reduced"],
    },
    "Afatinib": {
        "color": "#185FA5", "targets": ["EGFR"],
        "cascade": ["RAS","PI3K","RAF","AKT","MEK","STAT3"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "2nd-gen EGFR/HER2/HER4 TKI — irreversible pan-ErbB inhibitor",
        "cascade_text": ["EGFR + HER2/4 irreversibly blocked","→ RAS/MAPK suppressed","→ PI3K/AKT suppressed","→ STAT3 signaling reduced","→ Proliferation + Survival reduced"],
    },
    "Dacomitinib": {
        "color": "#185FA5", "targets": ["EGFR"],
        "cascade": ["RAS","PI3K","RAF","AKT","MEK"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "2nd-gen irreversible pan-HER TKI",
        "cascade_text": ["Pan-HER irreversibly blocked","→ RAS + PI3K suppressed","→ Proliferation + Survival reduced"],
    },
    "Mobocertinib": {
        "color": "#185FA5", "targets": ["EGFR"],
        "cascade": ["RAS","PI3K","RAF","AKT","MEK"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "EGFR exon 20 insertion-specific TKI",
        "cascade_text": ["EGFR exon20ins specifically blocked","→ RAS/PI3K suppressed","→ Proliferation + Survival reduced"],
    },
    "Amivantamab": {
        "color": "#0C447C", "targets": ["EGFR","MET"],
        "cascade": ["RAS","PI3K","AKT"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "Bispecific EGFR/MET antibody — blocks both receptors + immune activation",
        "cascade_text": ["EGFR + MET both blocked (antibody)","→ RAS + PI3K suppressed","→ Fc-mediated immune killing","→ Proliferation + Survival reduced"],
    },
    "Necitumumab": {
        "color": "#0C447C", "targets": ["EGFR"],
        "cascade": ["RAS","PI3K","RAF","AKT"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "Anti-EGFR monoclonal antibody — approved for squamous NSCLC",
        "cascade_text": ["EGFR ligand binding blocked","→ Receptor dimerization prevented","→ RAS + PI3K suppressed","→ Proliferation reduced"],
    },
 
    # ── MET inhibitors ───────────────────────────────────────
    "Tepotinib": {
        "color": "#639922", "targets": ["MET"],
        "cascade": ["RAS","PI3K","AKT","mTOR"],
        "outcomes": ["Cell survival"], "restored": [],
        "mechanism": "Selective MET inhibitor — MET exon14 skip & amplification",
        "cascade_text": ["MET amplification blocked","→ PI3K (via MET) suppressed","→ AKT/mTOR reduced","→ Cell survival weakened"],
    },
    "Capmatinib": {
        "color": "#3B6D11", "targets": ["MET"],
        "cascade": ["RAS","PI3K","AKT"],
        "outcomes": ["Cell survival"], "restored": [],
        "mechanism": "Selective MET inhibitor — FDA approved for MET exon14 skipping",
        "cascade_text": ["MET kinase blocked","→ PI3K arm suppressed","→ Cell survival reduced"],
    },
    "Crizotinib": {
        "color": "#D85A30", "targets": ["ALK","MET"],
        "cascade": ["RAS","PI3K","RAF","AKT"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "1st-gen ALK/MET/ROS1 inhibitor",
        "cascade_text": ["ALK + MET both inhibited","→ RAS / PI3K suppressed","→ Proliferation reduced"],
    },
 
    # ── ALK inhibitors ───────────────────────────────────────
    "Alectinib": {
        "color": "#D85A30", "targets": ["ALK"],
        "cascade": ["RAS","PI3K","RAF","AKT","MEK","ERK"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "2nd-gen ALK inhibitor — CNS penetrant, covers resistance mutations",
        "cascade_text": ["ALK fusion kinase blocked","→ RAS + PI3K both suppressed","→ RAF/MEK/ERK cascade drops","→ Proliferation + Cell survival reduced"],
    },
    "Lorlatinib": {
        "color": "#D85A30", "targets": ["ALK"],
        "cascade": ["RAS","PI3K","RAF","AKT","MEK","ERK"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "3rd-gen ALK/ROS1 inhibitor — overcomes all known resistance mutations",
        "cascade_text": ["ALK (3rd gen) blocked","→ Resistance mutations covered","→ RAS + PI3K suppressed","→ Proliferation + Survival reduced"],
    },
    "Brigatinib": {
        "color": "#D85A30", "targets": ["ALK"],
        "cascade": ["RAS","PI3K","RAF","AKT","MEK"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "2nd-gen ALK inhibitor — potent CNS activity",
        "cascade_text": ["ALK fusion blocked","→ RAS/PI3K suppressed","→ Proliferation + Survival reduced"],
    },
    "Ceritinib": {
        "color": "#D85A30", "targets": ["ALK"],
        "cascade": ["RAS","PI3K","RAF","AKT","MEK"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "2nd-gen ALK inhibitor — covers L1196M resistance",
        "cascade_text": ["ALK kinase blocked","→ RAS/PI3K suppressed","→ Proliferation reduced"],
    },
    "Repotrectinib": {
        "color": "#D85A30", "targets": ["ALK"],
        "cascade": ["RAS","PI3K","AKT"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "Next-gen ALK/ROS1/NTRK inhibitor — compact macrocyclic design",
        "cascade_text": ["ALK/ROS1 compactly inhibited","→ RAS + PI3K suppressed","→ Proliferation reduced"],
    },
 
    # ── RET inhibitors ───────────────────────────────────────
    "Selpercatinib": {
        "color": "#534AB7", "targets": ["RET"],
        "cascade": ["RAS","PI3K","AKT"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "Selective RET inhibitor — FDA approved RET fusion+ NSCLC",
        "cascade_text": ["RET fusion kinase blocked","→ RAS + PI3K suppressed","→ Proliferation + Survival reduced"],
    },
    "Pralsetinib": {
        "color": "#534AB7", "targets": ["RET"],
        "cascade": ["RAS","PI3K","AKT"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "Selective RET inhibitor — FDA approved, potent CNS penetration",
        "cascade_text": ["RET kinase selectively blocked","→ RAS/PI3K suppressed","→ Proliferation reduced"],
    },
    "Cabozantinib": {
        "color": "#534AB7", "targets": ["RET","MET"],
        "cascade": ["RAS","PI3K","AKT"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "Multi-kinase inhibitor — RET/MET/VEGFR2",
        "cascade_text": ["RET + MET + VEGFR2 blocked","→ Angiogenesis suppressed","→ RAS/PI3K reduced","→ Proliferation + Survival reduced"],
    },
 
    # ── NTRK inhibitors ──────────────────────────────────────
    "Larotrectinib": {
        "color": "#085041", "targets": ["NTRK"],
        "cascade": ["RAS","PI3K","AKT"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "Pan-TRK inhibitor — tumor-agnostic FDA approval",
        "cascade_text": ["NTRK fusion kinase blocked","→ RAS / PI3K signaling drops","→ Proliferation + Survival reduced"],
    },
    "Entrectinib": {
        "color": "#085041", "targets": ["NTRK"],
        "cascade": ["RAS","PI3K","AKT"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "Pan-TRK/ROS1/ALK inhibitor — CNS active",
        "cascade_text": ["NTRK/ROS1/ALK blocked","→ RAS/PI3K suppressed","→ Proliferation reduced"],
    },
 
    # ── KRAS inhibitors ──────────────────────────────────────
    "Sotorasib": {
        "color": "#854F0B", "targets": ["RAS"],
        "cascade": ["RAF","MEK","ERK"],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "KRAS G12C covalent inhibitor — locks KRAS in inactive GDP state",
        "cascade_text": ["KRAS G12C locked in inactive state","→ RAF cannot be recruited","→ MEK / ERK cascade drops","→ Proliferation reduced"],
    },
    "Adagrasib": {
        "color": "#854F0B", "targets": ["RAS"],
        "cascade": ["RAF","MEK","ERK"],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "KRAS G12C covalent inhibitor — longer half-life, CNS penetrant",
        "cascade_text": ["KRAS G12C covalently bound","→ Inactive GDP-locked state","→ RAF/MEK/ERK suppressed","→ Proliferation reduced"],
    },
 
    # ── BRAF inhibitors ──────────────────────────────────────
    "Dabrafenib": {
        "color": "#7F77DD", "targets": ["RAF"],
        "cascade": ["MEK","ERK"],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "BRAF V600E inhibitor — combine with MEK inhibitor to prevent bypass",
        "cascade_text": ["BRAF V600E blocked","→ MEK / ERK suppressed","→ Proliferation reduced","(Use with MEK inhibitor to prevent RAS bypass)"],
    },
    "Vemurafenib": {
        "color": "#7F77DD", "targets": ["RAF"],
        "cascade": ["MEK","ERK"],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "BRAF V600E inhibitor — 1st-gen, paradoxical activation risk",
        "cascade_text": ["BRAF V600E blocked","→ MEK/ERK suppressed","→ Proliferation reduced"],
    },
    "Encorafenib": {
        "color": "#7F77DD", "targets": ["RAF"],
        "cascade": ["MEK","ERK"],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "BRAF inhibitor — longer target residence time",
        "cascade_text": ["BRAF blocked (long residence)","→ MEK/ERK suppressed","→ Proliferation reduced"],
    },
    "Dabrafenib+Trametinib": {
        "color": "#7F77DD", "targets": ["RAF","MEK"],
        "cascade": ["ERK"],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "Dual BRAF+MEK blockade — prevents RAS feedback bypass",
        "cascade_text": ["BRAF blocked (Dabrafenib)","+ MEK blocked (Trametinib)","→ No feedback bypass possible","→ ERK fully suppressed","→ Proliferation blocked"],
    },
 
    # ── MEK inhibitors ───────────────────────────────────────
    "Trametinib": {
        "color": "#633806", "targets": ["MEK"],
        "cascade": ["ERK"],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "MEK1/2 inhibitor — blocks MAPK cascade downstream of RAS/RAF",
        "cascade_text": ["MEK1/2 blocked","→ ERK phosphorylation drops","→ MAPK output suppressed","→ Proliferation reduced"],
    },
    "Cobimetinib": {
        "color": "#633806", "targets": ["MEK"],
        "cascade": ["ERK"],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "MEK1/2 inhibitor — used with Vemurafenib for BRAF V600E",
        "cascade_text": ["MEK1/2 blocked","→ ERK suppressed","→ Proliferation reduced"],
    },
    "Binimetinib": {
        "color": "#633806", "targets": ["MEK"],
        "cascade": ["ERK"],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "MEK inhibitor — used with Encorafenib",
        "cascade_text": ["MEK blocked","→ ERK suppressed","→ Proliferation reduced"],
    },
    "Selumetinib": {
        "color": "#633806", "targets": ["MEK"],
        "cascade": ["ERK"],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "MEK1/2 inhibitor — NF1-associated tumors",
        "cascade_text": ["MEK1/2 blocked","→ ERK suppressed","→ Proliferation reduced"],
    },
 
    # ── CDK4/6 inhibitors ────────────────────────────────────
    "Palbociclib": {
        "color": "#3C3489", "targets": ["CDK4","CDK6"],
        "cascade": [],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "CDK4/6 inhibitor — blocks cell cycle G1→S transition",
        "cascade_text": ["CDK4/6 kinase blocked","→ RB remains unphosphorylated","→ G1 cell cycle arrest","→ Proliferation halted"],
    },
    "Ribociclib": {
        "color": "#3C3489", "targets": ["CDK4","CDK6"],
        "cascade": [],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "CDK4/6 inhibitor — selective G1 arrest",
        "cascade_text": ["CDK4/6 blocked","→ G1 arrest induced","→ Proliferation halted"],
    },
    "Abemaciclib": {
        "color": "#3C3489", "targets": ["CDK4","CDK6"],
        "cascade": [],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "CDK4/6 inhibitor — continuous dosing, monotherapy active",
        "cascade_text": ["CDK4/6 continuously blocked","→ G1 arrest","→ Proliferation halted"],
    },
 
    # ── PI3K/AKT/mTOR inhibitors ─────────────────────────────
    "Alpelisib": {
        "color": "#185FA5", "targets": ["PI3K"],
        "cascade": ["AKT","mTOR"],
        "outcomes": ["Cell survival","Proliferation"], "restored": [],
        "mechanism": "PI3Kα-specific inhibitor — PIK3CA mutant tumors",
        "cascade_text": ["PI3Kα blocked","→ AKT activation reduced","→ mTOR signaling drops","→ Cell survival + Proliferation reduced"],
    },
    "Capivasertib": {
        "color": "#185FA5", "targets": ["AKT"],
        "cascade": ["mTOR"],
        "outcomes": ["Cell survival"], "restored": [],
        "mechanism": "Pan-AKT inhibitor — AKT1/2/3 blockade",
        "cascade_text": ["AKT kinase blocked","→ mTOR signaling suppressed","→ Cell survival pathway reduced"],
    },
    "Everolimus": {
        "color": "#0C447C", "targets": ["mTOR"],
        "cascade": ["AKT"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "mTORC1 inhibitor (rapalog) — blocks protein synthesis and growth",
        "cascade_text": ["mTORC1 blocked","→ S6K/4EBP1 suppressed","→ Protein synthesis halted","→ Proliferation + Survival reduced"],
    },
    "Temsirolimus": {
        "color": "#0C447C", "targets": ["mTOR"],
        "cascade": ["AKT"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "mTORC1 inhibitor — IV formulation rapalog",
        "cascade_text": ["mTORC1 blocked","→ Protein synthesis suppressed","→ Proliferation + Survival reduced"],
    },
    "Copanlisib": {
        "color": "#185FA5", "targets": ["PI3K"],
        "cascade": ["AKT","mTOR"],
        "outcomes": ["Cell survival"], "restored": [],
        "mechanism": "Pan-PI3K inhibitor — IV administration, α/δ isoform preference",
        "cascade_text": ["PI3K (pan) blocked","→ AKT/mTOR suppressed","→ Cell survival reduced"],
    },
 
    # ── FGFR inhibitors ──────────────────────────────────────
    "Erdafitinib": {
        "color": "#3B6D11", "targets": ["FGFR1","FGFR2","FGFR3","FGFR4"],
        "cascade": ["PI3K","RAS","AKT"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "Pan-FGFR inhibitor — targets FGFR1-4 alterations",
        "cascade_text": ["FGFR kinase blocked","→ PI3K + RAS signaling reduced","→ Proliferation + Survival suppressed"],
    },
    "Pemigatinib": {
        "color": "#3B6D11", "targets": ["FGFR1","FGFR2","FGFR3"],
        "cascade": ["PI3K","RAS","AKT"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "Selective FGFR1/2/3 inhibitor",
        "cascade_text": ["FGFR1/2/3 selectively blocked","→ PI3K/RAS suppressed","→ Proliferation + Survival reduced"],
    },
    "Futibatinib": {
        "color": "#3B6D11", "targets": ["FGFR1","FGFR2","FGFR3","FGFR4"],
        "cascade": ["PI3K","AKT"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "Irreversible covalent pan-FGFR inhibitor",
        "cascade_text": ["FGFR irreversibly blocked","→ PI3K/AKT suppressed","→ Proliferation reduced"],
    },
 
    # ── PARP inhibitors ──────────────────────────────────────
    "Olaparib": {
        "color": "#712B13", "targets": ["BRCA1","BRCA2","ATM"],
        "cascade": [],
        "outcomes": ["Proliferation"], "restored": ["Apoptosis"],
        "mechanism": "PARP inhibitor — synthetic lethality in HRD tumors",
        "cascade_text": ["PARP enzyme blocked","→ DNA single-strand breaks unrepaired","→ BRCA-deficient cells cannot repair","→ Synthetic lethality → tumor death"],
    },
    "Rucaparib": {
        "color": "#712B13", "targets": ["BRCA1","BRCA2"],
        "cascade": [],
        "outcomes": ["Proliferation"], "restored": ["Apoptosis"],
        "mechanism": "PARP1/2/3 inhibitor — BRCA mutant tumors",
        "cascade_text": ["PARP blocked","→ DNA repair failure in HRD cells","→ Synthetic lethality","→ Tumor cell death"],
    },
    "Niraparib": {
        "color": "#712B13", "targets": ["BRCA1","BRCA2"],
        "cascade": [],
        "outcomes": ["Proliferation"], "restored": ["Apoptosis"],
        "mechanism": "PARP1/2 inhibitor — maintenance therapy, HRD tumors",
        "cascade_text": ["PARP1/2 blocked","→ HRD cells cannot repair DNA","→ Synthetic lethality","→ Tumor death"],
    },
    "Talazoparib": {
        "color": "#712B13", "targets": ["BRCA1","BRCA2"],
        "cascade": [],
        "outcomes": ["Proliferation"], "restored": ["Apoptosis"],
        "mechanism": "Potent PARP inhibitor + PARP trapping",
        "cascade_text": ["PARP trapped on DNA","→ Highly toxic to HRD cells","→ Synthetic lethality","→ Tumor death"],
    },
 
    # ── Immunotherapy ────────────────────────────────────────
    "Pembrolizumab": {
        "color": "#BA7517", "targets": ["T-cell"],
        "cascade": [],
        "outcomes": ["Cell survival"], "restored": ["Apoptosis"],
        "mechanism": "PD-1 checkpoint inhibitor — restores T-cell immune surveillance",
        "cascade_text": ["PD-1 on T-cell blocked","→ T-cells reactivated","→ Tumor cells recognized","→ Immune-mediated apoptosis restored"],
    },
    "Nivolumab": {
        "color": "#BA7517", "targets": ["T-cell"],
        "cascade": [],
        "outcomes": ["Cell survival"], "restored": ["Apoptosis"],
        "mechanism": "PD-1 checkpoint inhibitor — immune checkpoint blockade",
        "cascade_text": ["PD-1 blocked","→ T-cell exhaustion reversed","→ Anti-tumor immunity restored","→ Tumor apoptosis induced"],
    },
    "Atezolizumab": {
        "color": "#BA7517", "targets": ["T-cell"],
        "cascade": [],
        "outcomes": ["Cell survival"], "restored": ["Apoptosis"],
        "mechanism": "PD-L1 inhibitor — blocks PD-L1 on tumor cells",
        "cascade_text": ["PD-L1 on tumor blocked","→ T-cell inhibition removed","→ Anti-tumor immunity restored","→ Tumor apoptosis"],
    },
    "Durvalumab": {
        "color": "#BA7517", "targets": ["T-cell"],
        "cascade": [],
        "outcomes": ["Cell survival"], "restored": ["Apoptosis"],
        "mechanism": "PD-L1 inhibitor — approved for unresectable Stage III NSCLC",
        "cascade_text": ["PD-L1 blocked","→ T-cells reactivated","→ Tumor killing restored"],
    },
    "Cemiplimab": {
        "color": "#BA7517", "targets": ["T-cell"],
        "cascade": [],
        "outcomes": ["Cell survival"], "restored": ["Apoptosis"],
        "mechanism": "PD-1 inhibitor — approved for NSCLC first line (PD-L1 ≥50%)",
        "cascade_text": ["PD-1 blocked","→ T-cell immunity restored","→ Tumor apoptosis"],
    },
    "Avelumab": {
        "color": "#BA7517", "targets": ["T-cell"],
        "cascade": [],
        "outcomes": ["Cell survival"], "restored": ["Apoptosis"],
        "mechanism": "PD-L1 inhibitor — also activates ADCC",
        "cascade_text": ["PD-L1 blocked","→ T-cells reactivated","→ ADCC killing added","→ Tumor death"],
    },
    "Ipilimumab": {
        "color": "#633806", "targets": ["T-cell"],
        "cascade": [],
        "outcomes": ["Cell survival"], "restored": ["Apoptosis"],
        "mechanism": "CTLA-4 inhibitor — activates T-cells at priming phase",
        "cascade_text": ["CTLA-4 on T-cell blocked","→ T-cell activation amplified","→ Anti-tumor immunity boosted","→ Tumor apoptosis"],
    },
    "Tremelimumab": {
        "color": "#633806", "targets": ["T-cell"],
        "cascade": [],
        "outcomes": ["Cell survival"], "restored": ["Apoptosis"],
        "mechanism": "CTLA-4 inhibitor — used with Durvalumab (POSEIDON regimen)",
        "cascade_text": ["CTLA-4 blocked","→ T-cell priming enhanced","→ Synergy with PD-L1 blockade","→ Tumor apoptosis"],
    },
 
    # ── HER2 targeted ────────────────────────────────────────
    "Trastuzumab Deruxtecan": {
        "color": "#A32D2D", "targets": ["ERBB2"],
        "cascade": ["PI3K","RAS","AKT"],
        "outcomes": ["Proliferation","Cell survival"], "restored": ["Apoptosis"],
        "mechanism": "HER2-directed ADC — delivers topoisomerase inhibitor payload",
        "cascade_text": ["HER2 targeted by antibody","→ Drug payload delivered intracellularly","→ Topoisomerase I inhibited","→ DNA damage → tumor death"],
    },
    "Neratinib": {
        "color": "#A32D2D", "targets": ["ERBB2"],
        "cascade": ["RAS","PI3K","AKT"],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "Irreversible pan-HER TKI — HER2 mutant NSCLC",
        "cascade_text": ["HER2 irreversibly blocked","→ RAS/PI3K suppressed","→ Proliferation + Survival reduced"],
    },
 
    # ── MDM2 inhibitors ──────────────────────────────────────
    "Idasanutlin": {
        "color": "#5F5E5A", "targets": ["MDM2"],
        "cascade": ["TP53"],
        "outcomes": ["Proliferation"], "restored": ["Apoptosis"],
        "mechanism": "MDM2 inhibitor — restores TP53 function by blocking MDM2-TP53 interaction",
        "cascade_text": ["MDM2-TP53 interaction blocked","→ TP53 no longer degraded","→ TP53 function restored","→ Apoptosis re-enabled"],
    },
 
    # ── Chemotherapy ─────────────────────────────────────────
    "Paclitaxel": {
        "color": "#888780", "targets": [],
        "cascade": [],
        "outcomes": ["Proliferation"], "restored": ["Apoptosis"],
        "mechanism": "Taxane — stabilizes microtubules, blocks mitosis",
        "cascade_text": ["Microtubules stabilized","→ Mitotic spindle cannot depolymerize","→ Cell division blocked","→ Apoptosis induced"],
    },
    "Carboplatin": {
        "color": "#888780", "targets": [],
        "cascade": [],
        "outcomes": ["Proliferation"], "restored": ["Apoptosis"],
        "mechanism": "Platinum agent — crosslinks DNA, blocks replication",
        "cascade_text": ["DNA crosslinks formed","→ Replication blocked","→ Apoptosis induced"],
    },
    "Cisplatin": {
        "color": "#888780", "targets": [],
        "cascade": [],
        "outcomes": ["Proliferation"], "restored": ["Apoptosis"],
        "mechanism": "Platinum agent — DNA adduct formation",
        "cascade_text": ["DNA adducts formed","→ DNA replication blocked","→ Apoptosis induced"],
    },
    "Pemetrexed": {
        "color": "#888780", "targets": [],
        "cascade": [],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "Antifolate — inhibits thymidylate synthase, preferred in adenocarcinoma",
        "cascade_text": ["Folate metabolism blocked","→ DNA synthesis impaired","→ Proliferation reduced"],
    },
    "Bevacizumab": {
        "color": "#888780", "targets": [],
        "cascade": [],
        "outcomes": ["Proliferation","Cell survival"], "restored": [],
        "mechanism": "Anti-VEGF antibody — blocks angiogenesis",
        "cascade_text": ["VEGF-A neutralized","→ Tumor angiogenesis blocked","→ Tumor nutrient supply cut","→ Proliferation + Survival reduced"],
    },
    "Tazemetostat": {
        "color": "#5F5E5A", "targets": ["MDM2"],
        "cascade": [],
        "outcomes": ["Proliferation"], "restored": [],
        "mechanism": "EZH2 inhibitor — epigenetic therapy for ARID1A/SMARCA4 mutant tumors",
        "cascade_text": ["EZH2 methyltransferase blocked","→ H3K27me3 reduced","→ Tumor suppressor genes re-expressed","→ Proliferation reduced"],
    },
      "Bendamustine": {
        "color": "#888780", "targets": [],
        "cascade": [],
        "outcomes": ["Proliferation"], "restored": ["Apoptosis"],
        "mechanism": "Alkylating agent — DNA crosslinks, used in hematologic cancers",
        "cascade_text": ["DNA crosslinks formed","→ Replication blocked","→ Apoptosis induced"],
    },
    "Selinexor": {
        "color": "#5F5E5A", "targets": ["TP53"],
        "cascade": [],
        "outcomes": ["Proliferation"], "restored": ["Apoptosis"],
        "mechanism": "XPO1 inhibitor — traps TP53 in nucleus, restores tumor suppressor function",
        "cascade_text": ["XPO1 nuclear export blocked","→ TP53 retained in nucleus","→ TP53 transcriptional activity restored","→ Apoptosis re-enabled"],
    },
    "Alemtuzumab": {
        "color": "#888780", "targets": [],
        "cascade": [],
        "outcomes": ["Cell survival"], "restored": ["Apoptosis"],
        "mechanism": "Anti-CD52 monoclonal antibody — hematologic malignancies",
        "cascade_text": ["CD52 on lymphocytes targeted","→ ADCC + CDC killing","→ Tumor cell death"],
    },
    "Trabectedin": {
        "color": "#888780", "targets": [],
        "cascade": [],
        "outcomes": ["Proliferation"], "restored": ["Apoptosis"],
        "mechanism": "DNA minor groove binder — disrupts transcription factor binding",
        "cascade_text": ["DNA minor groove bound","→ Transcription factor binding blocked","→ DNA repair pathway hijacked","→ Apoptosis induced"],
    },
    "Ipatasertib": {
    "color": "#185FA5", "targets": ["AKT"],
    "cascade": ["mTOR"],
    "outcomes": ["Cell survival"], "restored": [],
    "mechanism": "AKT inhibitor — clinical trials for AKT1 mutant solid tumors",
    "cascade_text": [
        "AKT kinase blocked",
        "→ mTOR signaling suppressed",
        "→ Cell survival pathway reduced",
    ],
},
}

def build_cytoscape_elements(mutations_with_oncokb: list) -> tuple:
    """
    แสดงแค่ชื่อ gene บน node diagram
    ข้อมูล alteration/VAF แสดงที่ panel ขวามือแทน
    """
    mutated_genes = {m["gene"].upper() for m in mutations_with_oncokb}
 
    nodes = []
    for node_id, label, node_type, _ in PATHWAY_NODES:
        actual_type = "mutated" if node_id in mutated_genes else node_type
 
        # ── แสดงแค่ชื่อ gene — ไม่มี alteration/VAF ──────────
        display_label = node_id
        nodes.append({
            "data": {
                "id": node_id,
                "label": display_label,
                "type": actual_type,
                "isMutated": node_id in mutated_genes,
            }
        })
 
    edges = []
    for i, (src, tgt, edge_type) in enumerate(PATHWAY_EDGES):
        edges.append({
            "data": {
                "id": f"e{i}",
                "source": src,
                "target": tgt,
                "label": edge_type if edge_type in (
                    "degrades", "induces", "immune kill") else "",
            }
        })
 
    return nodes, edges

def build_drug_buttons(mutations_with_oncokb: list[dict]) -> list[dict]:
    seen = {}
    for mut in mutations_with_oncokb:
        oncokb = mut.get("oncokb", {})
        for tx in oncokb.get("treatments", []):
            drug_names = "+".join(d["drugName"] for d in tx.get("drugs", []))
            level = tx.get("level", "LEVEL_4")
            if drug_names not in seen:
                # ── normalize: Title Case ──────────────────────
                drug_display = drug_names.title()
                effects = DRUG_EFFECTS.get(drug_display) or \
                          DRUG_EFFECTS.get(drug_names) or \
                          DRUG_EFFECTS.get(drug_names.upper()) or {
                              "color": "#888780",
                              "targets": [],
                              "cascade": [],
                              "outcomes": [],
                              "restored": [],
                              "mechanism": f"Targets {mut['gene']} — see OncoKB for details",
                              "cascade_text": [],
                          }
                seen[drug_names] = {
                    "name": drug_display,
                    "level": level,
                    "gene": mut["gene"],
                    "effects": effects,
                }
    level_order = {"LEVEL_1":0,"LEVEL_2":1,"LEVEL_3A":2,"LEVEL_3B":3,"LEVEL_4":4}
    return sorted(seen.values(), key=lambda x: level_order.get(x["level"], 99))



def generate_pathway_html(mutations_with_oncokb: list[dict], patient_info: dict) -> str:
    """
    Main function — generate complete Cytoscape HTML
    ใส่ลงใน st.components.v1.html(html, height=700)
    """
    nodes, edges = build_cytoscape_elements(mutations_with_oncokb)
    drug_buttons = build_drug_buttons(mutations_with_oncokb)

    # Build patient summary สำหรับ default panel
    mut_summary = []
    outcome_summary = []
    for mut in mutations_with_oncokb:
        gene = mut["gene"]
        alt = mut.get("alteration", "")
        vaf = mut.get("vaf", "")
        oncokb = mut.get("oncokb", {})
        effect = oncokb.get("mutationEffect", "Unknown")
        desc = oncokb.get("description", "")[:120] + "..." if len(oncokb.get("description","")) > 120 else oncokb.get("description","")
        vaf_display = f"{float(vaf)*100:.0f}%" if vaf and str(vaf).replace('.','').isdigit() else str(vaf)
        mut_summary.append({
            "gene": gene, "alteration": alt,
            "vaf_display": vaf_display,
            "effect": effect, "desc": desc,
            "oncogenicity": oncokb.get("oncogenicity", "Unknown"),
        })

        # Outcome effects
        if "Gain-of-function" in effect:
            outcome_summary.append({"arrow": "↑", "color": "#A32D2D",
                "gene": "Proliferation / Cell survival",
                "desc": f"{gene} {alt} — overactivates downstream signaling"})
        if "Loss-of-function" in effect and gene == "TP53":
            outcome_summary.append({"arrow": "↓", "color": "#A32D2D",
                "gene": "Apoptosis",
                "desc": "TP53 inactivated — programmed cell death suppressed"})

    drug_rec_list = []
    for db in drug_buttons:
        drug_rec_list.append({
            "name": db["name"],
            "level": db["level"],
            "gene": db["gene"],
            "color": db["effects"].get("color", "#888"),
        })

    # Serialize ทุก data เป็น JSON
    nodes_json    = json.dumps(nodes)
    edges_json    = json.dumps(edges)
    drugs_json    = json.dumps({db["name"]: db["effects"] for db in drug_buttons})
    mut_json      = json.dumps(mut_summary)
    outcome_json  = json.dumps(outcome_summary)
    drug_rec_json = json.dumps(drug_rec_list)
    patient_json  = json.dumps(patient_info)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, sans-serif; }}
  body {{ background: #f8f8f6; }}
  #wrap {{ display: grid; grid-template-columns: 1fr 280px; height: 100vh; border: 1px solid #ddd; border-radius: 10px; overflow: hidden; background: white; }}
  #cy-side {{ position: relative; background: #f4f3f0; }}
  #cy {{ width: 100%; height: 100%; }}
  #top-bar {{ position: absolute; top: 10px; left: 10px; right: 10px; display: flex; gap: 5px; flex-wrap: wrap; z-index: 10; align-items: center; }}
  .drug-btn {{ font-size: 11px; padding: 4px 10px; border-radius: 99px; border: 1px solid #ccc; background: white; cursor: pointer; transition: all .15s; }}
  .drug-btn:hover {{ background: #f0f0ee; }}
  .drug-btn.active {{ font-weight: 600; }}
  #legend-bar {{ position: absolute; bottom: 10px; left: 10px; display: flex; gap: 10px; flex-wrap: wrap; z-index: 10; }}
  .leg {{ display: flex; align-items: center; gap: 4px; font-size: 10px; color: #666; }}
  .ld {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
  #right {{ border-left: 1px solid #e8e8e6; display: flex; flex-direction: column; overflow: hidden; }}
  #pt-header {{ padding: 12px 14px; border-bottom: 1px solid #e8e8e6; background: #f8f8f6; }}
  .pt-label {{ font-size: 10px; font-weight: 600; color: #999; letter-spacing: .06em; text-transform: uppercase; margin-bottom: 5px; }}
  .pt-name {{ font-size: 14px; font-weight: 600; color: #1a1a1a; }}
  .pt-sub {{ font-size: 11px; color: #666; margin-top: 2px; }}
  .badges {{ display: flex; gap: 4px; margin-top: 6px; flex-wrap: wrap; }}
  .badge {{ font-size: 10px; padding: 2px 7px; border-radius: 99px; }}
  .badge-blue {{ background: #e6f1fb; color: #0c447c; }}
  .badge-amber {{ background: #faeeda; color: #633806; }}
  #scroll-area {{ flex: 1; overflow-y: auto; padding: 12px 14px; display: flex; flex-direction: column; gap: 10px; }}
  .sec-title {{ font-size: 10px; font-weight: 600; color: #999; letter-spacing: .06em; text-transform: uppercase; margin-bottom: 5px; }}
  .card {{ background: #f8f8f6; border-radius: 8px; padding: 9px 11px; }}
  .mut-row {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 7px; padding-bottom: 7px; border-bottom: 1px solid #e8e8e6; }}
  .mut-row:last-child {{ border-bottom: none; margin: 0; padding: 0; }}
  .gene-name {{ font-size: 12px; font-weight: 600; color: #1a1a1a; }}
  .gene-alt {{ font-size: 10px; color: #888; margin-top: 1px; }}
  .gene-desc {{ font-size: 10px; color: #666; margin-top: 3px; line-height: 1.4; }}
  .vaf-val {{ font-size: 12px; font-weight: 600; color: #a32d2d; }}
  .vaf-label {{ font-size: 10px; color: #999; }}
  .out-row {{ display: flex; gap: 7px; align-items: flex-start; margin-bottom: 6px; padding-bottom: 6px; border-bottom: 1px solid #e8e8e6; }}
  .out-row:last-child {{ border-bottom: none; margin: 0; padding: 0; }}
  .out-arr {{ font-size: 14px; line-height: 1.2; flex-shrink: 0; }}
  .out-gene {{ font-size: 12px; font-weight: 600; color: #1a1a1a; }}
  .out-desc {{ font-size: 11px; color: #666; line-height: 1.4; margin-top: 1px; }}
  .rec-row {{ display: flex; align-items: center; gap: 7px; margin-bottom: 6px; padding-bottom: 6px; border-bottom: 1px solid #e8e8e6; cursor: pointer; }}
  .rec-row:last-child {{ border-bottom: none; margin: 0; padding: 0; }}
  .rec-row:hover {{ opacity: .8; }}
  .rec-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
  .rec-name {{ font-size: 12px; font-weight: 600; color: #1a1a1a; }}
  .rec-why {{ font-size: 10px; color: #888; margin-top: 1px; }}
  .dd-name {{ font-size: 13px; font-weight: 600; color: #1a1a1a; margin-bottom: 3px; }}
  .dd-target {{ font-size: 11px; color: #666; margin-bottom: 8px; line-height: 1.5; }}
  .eff-row {{ display: flex; gap: 7px; align-items: flex-start; margin-bottom: 6px; padding-bottom: 6px; border-bottom: 1px solid #e8e8e6; }}
  .eff-row:last-child {{ border-bottom: none; margin: 0; padding: 0; }}
  .eff-arr {{ font-size: 14px; line-height: 1; flex-shrink: 0; }}
  .eff-gene {{ font-size: 12px; font-weight: 600; color: #1a1a1a; }}
  .eff-desc {{ font-size: 11px; color: #666; line-height: 1.4; }}
  .cas-box {{ background: white; border-radius: 6px; padding: 8px 10px; margin-top: 6px; border: 1px solid #e8e8e6; }}
  .cas-title {{ font-size: 10px; color: #999; margin-bottom: 4px; }}
  .cas-step {{ font-size: 11px; color: #666; padding: 1px 0; }}
  .warn {{ background: #faeeda; border-radius: 6px; padding: 8px 10px; margin-top: 6px; font-size: 11px; color: #633806; line-height: 1.5; }}
  .lvl-1 {{ background: #eaf3de; color: #27500a; }}
  .lvl-2 {{ background: #e6f1fb; color: #0c447c; }}
  .lvl-3a {{ background:#FAEEDA; color:#633806; }}
  .lvl-4  {{ background:#F1EFE8; color:#5F5E5A; }}
  .lvl-r  {{ background:#FCEBEB; color:#791F1F; }}
</style>
</head>
<body>
<div id="wrap">
  <div id="cy-side">
    <div id="top-bar">
      <span style="font-size:11px;color:#999;flex-shrink:0;">Drug:</span>
      <button class="drug-btn active" id="btn-none" onclick="selectDrug(null,this)" style="background:#f0f0ee;border-color:#999;">Patient overview</button>
      <span id="drug-btns"></span>
    </div>
    <div id="cy"></div>
    <div id="legend-bar">
      <div class="leg"><div class="ld" style="background:#E24B4A;"></div>Mutated</div>
      <div class="leg"><div class="ld" style="background:#888780;"></div>Signaling</div>
      <div class="leg"><div class="ld" style="background:#1D9E75;border-radius:3px;"></div>Suppressor</div>
      <div class="leg"><div class="ld" style="background:#BA7517;border-radius:3px;"></div>Outcome</div>
      <div class="leg" id="leg-drug" style="display:none;"><div class="ld" style="background:#378ADD;outline:2px solid #378ADD;outline-offset:2px;"></div>Drug target</div>
      <div class="leg" id="leg-cas" style="display:none;"><div class="ld" style="background:#7F77DD;"></div>Cascade</div>
    </div>
  </div>
  <div id="right">
    <div id="pt-header">
      <div class="pt-label">Patient file</div>
      <div class="pt-name" id="pt-name">—</div>
      <div class="pt-sub" id="pt-sub">—</div>
      <div class="badges" id="pt-badges"></div>
    </div>
    <div id="scroll-area"><div id="right-content"></div></div>
  </div>
</div>

<script>
const NODES = {nodes_json};
const EDGES = {edges_json};
const DRUGS = {drugs_json};
const MUTS  = {mut_json};
const OUTCOMES = {outcome_json};
const DRUG_RECS = {drug_rec_json};
const PATIENT = {patient_json};

const C = {{
  mutated:   {{bg:'#E24B4A', bd:'#A32D2D'}},
  receptor:  {{bg:'#378ADD', bd:'#185FA5'}},
  signaling: {{bg:'#888780', bd:'#5F5E5A'}},
  suppressor:{{bg:'#1D9E75', bd:'#0F6E56'}},
  outcome:   {{bg:'#BA7517', bd:'#854F0B'}},
  immune:    {{bg:'#1D9E75', bd:'#0F6E56'}},
}};

// ─── Init patient header ─────────────────────────────────────────────────────
document.getElementById('pt-name').textContent  = PATIENT.name || 'Patient';
document.getElementById('pt-sub').textContent   = PATIENT.subtitle || '';
const bCont = document.getElementById('pt-badges');
(PATIENT.badges || []).forEach(b => {{
  const s = document.createElement('span');
  s.className = 'badge ' + (b.cls || 'badge-blue');
  s.textContent = b.text;
  bCont.appendChild(s);
}});

// ─── Build drug buttons ──────────────────────────────────────────────────────
const dbCont = document.getElementById('drug-btns');
DRUG_RECS.forEach(dr => {{
  const btn = document.createElement('button');
  btn.className = 'drug-btn';
  btn.id = 'btn-' + dr.name.replace(/[^a-z0-9]/gi,'_');
  btn.textContent = dr.name;
   const lvlClass =
    dr.level === 'LEVEL_1'  ? 'lvl-1'  :
    dr.level === 'LEVEL_2'  ? 'lvl-2'  :
    dr.level === 'LEVEL_3A' ? 'lvl-3a' :
    dr.level === 'LEVEL_3B' ? 'lvl-3a' :
    dr.level === 'LEVEL_4'  ? 'lvl-4'  :
    dr.level === 'LEVEL_R1' ? 'lvl-r'  : 'lvl-4';
  btn.setAttribute('data-level', dr.level);
  btn.setAttribute('data-color', dr.color);
  btn.onclick = function(){{ selectDrug(dr.name, this); }};
  dbCont.appendChild(btn);
}});

// ─── Cytoscape init ──────────────────────────────────────────────────────────
const cy = cytoscape({{
  container: document.getElementById('cy'),
  elements: [...NODES, ...EDGES],
  style: [
    {{ selector: 'node', style: {{
      'label': 'data(label)', 'text-valign': 'center', 'text-halign': 'center',
      'font-size': '11px', 'font-family': 'sans-serif', 'text-wrap': 'wrap',
      'color': '#fff', 'width': 62, 'height': 62, 'shape': 'ellipse',
      'background-color': ele => C[ele.data('type')]?.bg || '#888',
      'border-width': 2,
      'border-color': ele => C[ele.data('type')]?.bd || '#555',
      'transition-property': 'background-color,border-color,border-width,opacity',
      'transition-duration': '0.22s',
    }}}},
    {{ selector: 'node[type="outcome"]',   style: {{'shape':'round-rectangle','width':80,'height':44}} }},
    {{ selector: 'node[type="immune"]',    style: {{'shape':'round-rectangle','width':76,'height':44}} }},
    {{ selector: 'node[type="suppressor"]',style: {{'shape':'diamond','width':70,'height':70}} }},
    {{ selector: 'edge', style: {{
      'width': 1.5, 'line-color': '#ccc', 'target-arrow-color': '#ccc',
      'target-arrow-shape': 'triangle', 'curve-style': 'bezier',
      'font-size': '9px', 'label': 'data(label)', 'color': '#999',
      'transition-property': 'line-color,target-arrow-color,width,opacity',
      'transition-duration': '0.22s',
    }}}},
  ],
  layout: {{ name: 'cose', animate: false, nodeRepulsion: 9500, idealEdgeLength: 100, gravity: 0.4, padding: 60 }}
}});

cy.on('tap', 'node', function(evt) {{
  const id = evt.target.id();

  const nodeInfo = {{
    'EGFR':   {{desc: 'EGFR — receptor tyrosine kinase, activates RAS & PI3K pathways'}},
    'MET':    {{desc: 'MET — hepatocyte growth factor receptor, bypass pathway'}},
    'ALK':    {{desc: 'ALK — fusion oncogene, ~5% NSCLC'}},
    'RAS':    {{desc: 'RAS — central signal relay downstream of EGFR/MET/ALK'}},
    'RAF':    {{desc: 'RAF — MAPK cascade step 1, activated by RAS'}},
    'MEK':    {{desc: 'MEK1/2 — MAPK cascade step 2'}},
    'ERK':    {{desc: 'ERK — transcription factor activator, drives proliferation'}},
    'PI3K':   {{desc: 'PI3K Class 1A — survival signaling hub'}},
    'AKT':    {{desc: 'AKT — master survival kinase'}},
    'mTOR':   {{desc: 'mTORC1/2 — controls protein synthesis & growth'}},
    'MDM2':   {{desc: 'MDM2 — degrades TP53 (AKT activates MDM2)'}},
    'TP53':   {{desc: 'TP53 — tumor suppressor, induces apoptosis when mutated → inactivated'}},
    'STAT3':  {{desc: 'STAT3 — transcription factor, activated by JAK'}},
    'JAK':    {{desc: 'JAK — activated by EGFR, phosphorylates STAT3'}},
    'T-cell': {{desc: 'T-cell (immune) — kills tumor cells via PD-1/PD-L1 checkpoint'}},
    'Proliferation': {{desc: 'Outcome: uncontrolled tumor cell division'}},
    'Cell survival': {{desc: 'Outcome: tumor evades apoptosis'}},
    'Apoptosis':     {{desc: 'Outcome: programmed cell death (suppressed by mutations)'}},
    'ROS1':   {{desc: 'ROS1 — fusion oncogene, ~2% NSCLC, TKI-sensitive'}},
    'RET':    {{desc: 'RET — fusion oncogene, ~2% NSCLC, selective TKI available'}},
    'FGFR1':  {{desc: 'FGFR1 — amplified in ~20% squamous NSCLC'}},
    'FGFR2':  {{desc: 'FGFR2 — FGFR pathway alteration'}},
    'FGFR3':  {{desc: 'FGFR3 — FGFR pathway, fusion or mutation'}},
    'NTRK':   {{desc: 'NTRK fusion — tumor-agnostic TRK inhibitor indication'}},
    'BRCA1':  {{desc: 'BRCA1 — DNA repair (HRR), loss → PARP inhibitor sensitive'}},
    'BRCA2':  {{desc: 'BRCA2 — DNA repair (HRR), loss → PARP inhibitor sensitive'}},
    'ATM':    {{desc: 'ATM — DNA damage response, loss → HRD phenotype'}},
    'CDK4':   {{desc: 'CDK4 — cell cycle kinase, amplification drives G1→S'}},
    'CDK6':   {{desc: 'CDK6 — CDK4/6 complex, cell cycle progression'}},
    'PIK3CA': {{desc: 'PIK3CA — PI3K catalytic subunit, activating mutations common'}},
    'PTEN':   {{desc: 'PTEN — PI3K suppressor, loss hyperactivates AKT'}},
    'NF1':    {{desc: 'NF1 — RAS GTPase activator, loss hyperactivates RAS'}},
    'ERBB2':  {{desc: 'ERBB2 (HER2) — ~3% NSCLC, T-DXd FDA approved'}},
    'STK11':  {{desc: 'STK11 — tumor suppressor, loss → immunotherapy resistance'}},
    'KEAP1':  {{desc: 'KEAP1 — oxidative stress regulator, loss → poor TKI response'}},
    'MAP2K1': {{desc: 'MAP2K1 (MEK1) — MAPK cascade, MEK inhibitor target'}},
    'MAP2K2': {{desc: 'MAP2K2 (MEK2) — MAPK cascade'}},
    'CDK4':   {{desc: 'CDK4 — cell cycle kinase, CDK4/6 inhibitor target'}},
    'CDKN2A': {{desc: 'CDKN2A — CDK inhibitor, loss releases CDK4/6'}},
    'POLE':   {{desc: 'POLE — DNA polymerase, mutations → ultra-high TMB → immunotherapy'}},
    'SMARCA4':{{desc: 'SMARCA4 — chromatin remodeling, SWI/SNF complex'}},
    'ARID1A': {{desc: 'ARID1A — SWI/SNF complex, tumor suppressor'}},
    'MYC':    {{desc: 'MYC — transcription factor, amplification drives proliferation'}},
    'PDCD1':  {{desc: 'PDCD1 (PD-1) — immune checkpoint on T-cells'}},
    'CD274':  {{desc: 'CD274 (PD-L1) — immune evasion on tumor cells'}},
  }};

  const isMutated = evt.target.data('isMutated');
  const mut  = MUTS.find(m => m.gene === id);
  const info = nodeInfo[id];

  const existing = document.querySelector('.node-popup');
  if (existing) existing.remove();

  const box = document.createElement('div');
  box.className = 'card node-popup';
  box.style.marginTop = '8px';

  if (isMutated && mut) {{
    box.innerHTML = `
      <div class="gene-name" style="color:#a32d2d;">${{id}} — Mutated</div>
      <div class="gene-alt">${{mut.alteration}} | VAF: ${{mut.vaf_display}} | ${{mut.oncogenicity}}</div>
      <div class="gene-desc" style="margin-top:4px;">${{mut.desc}}</div>`;
  }} else if (info) {{
    box.innerHTML = `
      <div class="gene-name">${{id}}</div>
      <div class="gene-desc" style="margin-top:4px;">${{info.desc}}</div>`;
  }} else {{
    return;
  }}

  document.getElementById('right-content').prepend(box);
}});

// ─── Reset graph ─────────────────────────────────────────────────────────────
function resetGraph() {{
  cy.nodes().forEach(n => {{
    const c = C[n.data('type')] || C.signaling;
    n.style({{'background-color':c.bg,'border-color':c.bd,'border-width':2,'opacity':1}});
  }});
  cy.edges().forEach(e => e.style({{'line-color':'#ccc','target-arrow-color':'#ccc','width':1.5,'opacity':1}}));
  document.getElementById('leg-drug').style.display = 'none';
  document.getElementById('leg-cas').style.display  = 'none';
}}

// ─── Select drug ─────────────────────────────────────────────────────────────
function selectDrug(id, btn) {{
  document.querySelectorAll('.drug-btn').forEach(b => {{
    b.classList.remove('active');
    b.style.background = 'white';
    b.style.borderColor = '#ccc';
  }});
  resetGraph();
  document.querySelector('.node-popup')?.remove();

  if (!id) {{
    btn.classList.add('active');
    btn.style.background = '#f0f0ee';
    btn.style.borderColor = '#999';
    renderPatientOverview();
    return;
  }}

  btn.classList.add('active');
  const d = DRUGS[id];
  if (!d) return;
  btn.style.background = d.color + '22';
  btn.style.borderColor = d.color;

  // Dim all
  cy.nodes().forEach(n => n.style({{'opacity': 0.14}}));
  cy.edges().forEach(e => e.style({{'opacity': 0.07}}));

  // Highlight drug targets
  (d.targets||[]).forEach(gid => {{
    cy.getElementById(gid).style({{'background-color':d.color,'border-color':d.color,'border-width':4,'opacity':1}});
  }});
  // Cascade
  (d.cascade||[]).forEach(gid => {{
    cy.getElementById(gid).style({{'background-color':'#7F77DD','border-color':'#534AB7','border-width':2,'opacity':0.88}});
  }});
  // Outcomes
  (d.outcomes||[]).forEach(gid => {{
    cy.getElementById(gid).style({{'background-color':'#534AB7','border-color':'#3C3489','border-width':3,'opacity':1}});
  }});
  // Restored
  (d.restored||[]).forEach(gid => {{
    cy.getElementById(gid).style({{'background-color':'#1D9E75','border-color':'#0F6E56','border-width':3,'opacity':1}});
  }});

  // Active edges
  const active = new Set([...(d.targets||[]),...(d.cascade||[]),...(d.outcomes||[]),...(d.restored||[])]);
  cy.edges().forEach(e => {{
    if (active.has(e.data('source')) && active.has(e.data('target')))
      e.style({{'line-color':d.color,'target-arrow-color':d.color,'width':2.5,'opacity':1}});
  }});

  document.getElementById('leg-drug').style.display = 'flex';
  document.getElementById('leg-cas').style.display  = 'flex';
  renderDrugDetail(id, d);
}}

// ─── Render panels ───────────────────────────────────────────────────────────
function renderPatientOverview() {{
  let html = '';
  html += `<div class="sec-title">Mutations detected (${{MUTS.length}})</div><div class="card">`;
  MUTS.forEach(m => {{
    html += `<div class="mut-row">
      <div><div class="gene-name">${{m.gene}} <span style="color:#a32d2d;font-size:10px;">● ${{m.oncogenicity}}</span></div>
      <div class="gene-alt">${{m.alteration}} — ${{m.effect}}</div>
      <div class="gene-desc">${{m.desc}}</div></div>
      <div style="text-align:right;flex-shrink:0;margin-left:8px;"><div class="vaf-val">${{m.vaf_display}}</div><div class="vaf-label">VAF</div></div>
    </div>`;
  }});
  html += `</div>`;

  if (OUTCOMES.length) {{
    html += `<div class="sec-title" style="margin-top:2px;">Pathway outcomes</div><div class="card">`;
    OUTCOMES.forEach(o => {{
      html += `<div class="out-row"><span class="out-arr" style="color:${{o.color}}">${{o.arrow}}</span>
        <div><div class="out-gene">${{o.gene}}</div><div class="out-desc">${{o.desc}}</div></div></div>`;
    }});
    html += `</div>`;
  }}

  html += `<div class="sec-title" style="margin-top:2px;">Drug recommendations</div><div class="card">`;
  DRUG_RECS.forEach(dr => {{
    const lvlClass =
    dr.level==='LEVEL_1'  ? 'lvl-1'  :
    dr.level==='LEVEL_2'  ? 'lvl-2'  :
    dr.level==='LEVEL_3A' ? 'lvl-3a' :
    dr.level==='LEVEL_3B' ? 'lvl-3a' :
    dr.level==='LEVEL_4'  ? 'lvl-4'  :
    dr.level==='LEVEL_R1' ? 'lvl-r'  : 'lvl-4';
  const lvlDotColors = {{
    'LEVEL_1':'#27500A','LEVEL_2':'#0C447C',
    'LEVEL_3A':'#633806','LEVEL_3B':'#633806',
    'LEVEL_4':'#5F5E5A','LEVEL_R1':'#791F1F'
  }};
    html += `<div class="rec-row" onclick="document.getElementById('btn-${{dr.name.replace(/[^a-z0-9]/gi,'_')}}')?.click()">
      <div class="rec-dot" style="background:${{dr.color}}"></div>
      <div><div class="rec-name">${{dr.name}}</div>
      <div class="rec-why"><span class="badge ${{lvlClass}}" style="font-size:9px;padding:1px 5px;">${{dr.level.replace('_',' ')}}</span>  targets ${{dr.gene}}</div></div>
    </div>`;
  }});
  html += `</div>`;
  document.getElementById('right-content').innerHTML = html;
}}

function renderDrugDetail(id, d) {{
  const effects_map = {{
    'targets':  {{arrow:'↓', color:'#a32d2d', suffix:'directly inhibited'}},
    'cascade':  {{arrow:'↓', color:'#534AB7', suffix:'suppressed (cascade)'}},
    'outcomes': {{arrow:'↓', color:'#a32d2d', suffix:'reduced'}},
    'restored': {{arrow:'↑', color:'#27500a', suffix:'restored'}},
  }};

  let html = `<div class="dd-name">${{id}}</div><div class="dd-target">${{d.mechanism}}</div>`;

  ['targets','cascade','outcomes','restored'].forEach(k => {{
    const nodes = d[k] || [];
    if (!nodes.length) return;
    const em = effects_map[k];
    nodes.forEach(g => {{
      html += `<div class="eff-row">
        <span class="eff-arr" style="color:${{em.color}}">${{em.arrow}}</span>
        <div><div class="eff-gene">${{g}}</div>
        <div class="eff-desc">${{em.suffix}}</div></div></div>`;
    }});
  }});

  if ((d.cascade_text||[]).length) {{
    html += `<div class="cas-box"><div class="cas-title">Cascade effect</div>`;
    d.cascade_text.forEach((s,i) => {{
      html += `<div class="cas-step" style="padding-left:${{i>0?10:0}}px">${{s}}</div>`;
    }});
    html += `</div>`;
  }}
  document.getElementById('right-content').innerHTML = `<div class="card">${{html}}</div>`;
}}

// ─── Init ─────────────────────────────────────────────────────────────────────
setTimeout(() => {{
  renderPatientOverview();
}}, 100);
</script>
</body>
</html>"""

    return html
