"""
oncokb_client.py
────────────────
Query OncoKB API สำหรับ mutation → drug recommendation
Register token ฟรีได้ที่: https://oncokb.org/account
"""

import requests
import os

ONCOKB_TOKEN = os.environ.get("ONCOKB_TOKEN", "YOUR_TOKEN_HERE")
BASE_URL = "https://www.oncokb.org/api/v1"

HEADERS = {
    "Authorization": f"Bearer {ONCOKB_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# ─── Fallback local database (ใช้เมื่อไม่มี token หรือ offline) ───────────────
LOCAL_DB = {
    ("EGFR", "L858R"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Osimertinib"}], "level": "LEVEL_1",
             "pmids": ["28168010"], "approvedIndications": ["Lung Adenocarcinoma"]},
            {"drugs": [{"drugName": "Erlotinib"}], "level": "LEVEL_1",
             "pmids": ["15118073"], "approvedIndications": ["NSCLC"]},
        ],
        "description": "EGFR L858R is the most common activating mutation in NSCLC, "
                       "found predominantly in Asian patients (~40%) and non-smokers.",
    },
    ("EGFR", "T790M"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Osimertinib"}], "level": "LEVEL_1",
             "pmids": ["26559455"], "approvedIndications": ["NSCLC - resistance"]},
        ],
        "description": "T790M is the primary resistance mechanism after 1st/2nd gen EGFR TKI.",
    },
    ("KRAS", "G12C"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Sotorasib"}], "level": "LEVEL_1",
             "pmids": ["34096690"], "approvedIndications": ["NSCLC"]},
            {"drugs": [{"drugName": "Adagrasib"}], "level": "LEVEL_1",
             "pmids": ["35290258"], "approvedIndications": ["NSCLC"]},
        ],
        "description": "KRAS G12C mutation found in ~13% of lung adenocarcinoma.",
    },
    ("ALK", "Fusion"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Alectinib"}], "level": "LEVEL_1",
             "pmids": ["27573585"], "approvedIndications": ["ALK+ NSCLC"]},
            {"drugs": [{"drugName": "Crizotinib"}], "level": "LEVEL_1",
             "pmids": ["21830448"], "approvedIndications": ["ALK+ NSCLC"]},
        ],
        "description": "ALK fusions occur in ~5% of NSCLC, common in younger non-smokers.",
    },
    ("MET", "Amplification"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Tepotinib"}], "level": "LEVEL_2",
             "pmids": ["32469183"], "approvedIndications": ["MET exon14 NSCLC"]},
            {"drugs": [{"drugName": "Capmatinib"}], "level": "LEVEL_2",
             "pmids": ["32469182"], "approvedIndications": ["MET exon14 NSCLC"]},
        ],
        "description": "MET amplification is a primary resistance bypass after EGFR TKI therapy.",
    },
    ("TP53", "R248W"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_4",
        "treatments": [],  # ยังไม่มี direct approved therapy
        "description": "TP53 R248W inactivates tumor suppressor. No direct targeted therapy; "
                       "affects prognosis and immunotherapy response.",
    },
    ("BRAF", "V600E"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Dabrafenib"}, {"drugName": "Trametinib"}],
             "level": "LEVEL_1", "pmids": ["26743496"],
             "approvedIndications": ["BRAF V600E NSCLC"]},
        ],
        "description": "BRAF V600E found in ~2% NSCLC. Combination BRAF+MEK inhibition required "
                       "to prevent RAS-mediated feedback bypass.",
    },
    ("RET", "Fusion"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Selpercatinib"}], "level": "LEVEL_1",
             "pmids": ["32846071"], "approvedIndications": ["RET fusion+ NSCLC"]},
        ],
        "description": "RET fusions in ~2% NSCLC. Highly sensitive to selective RET inhibitors.",
    },
    ("EGFR", "L858R"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Osimertinib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
            {"drugs": [{"drugName": "Erlotinib"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
            {"drugs": [{"drugName": "Afatinib"}],     "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
            {"drugs": [{"drugName": "Gefitinib"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
            {"drugs": [{"drugName": "Dacomitinib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
        ],
        "description": "EGFR L858R — most common activating mutation, ~40% in Asian NSCLC.",
    },
    ("EGFR", "T790M"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Osimertinib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
        ],
        "description": "EGFR T790M — resistance mutation after 1st/2nd gen TKI.",
    },
    ("EGFR", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Osimertinib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
            {"drugs": [{"drugName": "Afatinib"}],      "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
            {"drugs": [{"drugName": "Mobocertinib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
            {"drugs": [{"drugName": "Necitumumab"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["Squamous NSCLC"]},
            {"drugs": [{"drugName": "Amivantamab"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["EGFR exon20 NSCLC"]},
        ],
        "description": "EGFR — receptor tyrosine kinase, activates RAS & PI3K pathways.",
    },
 
    # ══════════════════════════════════════════════════════════
    # KRAS
    # ══════════════════════════════════════════════════════════
    ("KRAS", "G12C"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Sotorasib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
            {"drugs": [{"drugName": "Adagrasib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
        ],
        "description": "KRAS G12C — ~13% lung adenocarcinoma. Covalent G12C inhibitors available.",
    },
    ("KRAS", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Sotorasib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["KRAS G12C NSCLC"]},
            {"drugs": [{"drugName": "Adagrasib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["KRAS G12C NSCLC"]},
        ],
        "description": "KRAS — central RAS oncogene. G12C-specific inhibitors FDA approved.",
    },
 
    # ══════════════════════════════════════════════════════════
    # ALK
    # ══════════════════════════════════════════════════════════
    ("ALK", "Fusion"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Alectinib"}],     "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ALK+ NSCLC"]},
            {"drugs": [{"drugName": "Lorlatinib"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ALK+ NSCLC"]},
            {"drugs": [{"drugName": "Brigatinib"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ALK+ NSCLC"]},
            {"drugs": [{"drugName": "Crizotinib"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ALK+ NSCLC"]},
            {"drugs": [{"drugName": "Ceritinib"}],     "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ALK+ NSCLC"]},
        ],
        "description": "ALK fusion — ~5% NSCLC. Highly sensitive to ALK inhibitors.",
    },
    ("ALK", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Alectinib"}],     "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ALK+ NSCLC"]},
            {"drugs": [{"drugName": "Lorlatinib"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ALK+ NSCLC"]},
            {"drugs": [{"drugName": "Brigatinib"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ALK+ NSCLC"]},
            {"drugs": [{"drugName": "Crizotinib"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ALK+ NSCLC"]},
            {"drugs": [{"drugName": "Ceritinib"}],     "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ALK+ NSCLC"]},
        ],
        "description": "ALK — fusion oncogene in ~5% NSCLC.",
    },
 
    # ══════════════════════════════════════════════════════════
    # MET
    # ══════════════════════════════════════════════════════════
    ("MET", "Amplification"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Tepotinib"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["MET exon14 NSCLC"]},
            {"drugs": [{"drugName": "Capmatinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["MET exon14 NSCLC"]},
            {"drugs": [{"drugName": "Crizotinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["MET+ NSCLC"]},
        ],
        "description": "MET amplification — bypass resistance after EGFR TKI.",
    },
    ("MET", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Tepotinib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["MET exon14 NSCLC"]},
            {"drugs": [{"drugName": "Capmatinib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["MET exon14 NSCLC"]},
            {"drugs": [{"drugName": "Crizotinib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["MET+ NSCLC"]},
            {"drugs": [{"drugName": "Amivantamab"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["MET/EGFR NSCLC"]},
        ],
        "description": "MET — hepatocyte growth factor receptor, bypass pathway activator.",
    },
 
    # ══════════════════════════════════════════════════════════
    # BRAF
    # ══════════════════════════════════════════════════════════
    ("BRAF", "V600E"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Dabrafenib"}, {"drugName": "Trametinib"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["BRAF V600E NSCLC"]},
            {"drugs": [{"drugName": "Dabrafenib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["BRAF V600E NSCLC"]},
        ],
        "description": "BRAF V600E — ~2% NSCLC. Combination BRAF+MEK inhibition required.",
    },
    ("BRAF", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Dabrafenib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["BRAF V600E NSCLC"]},
            {"drugs": [{"drugName": "Trametinib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["BRAF V600E NSCLC"]},
            {"drugs": [{"drugName": "Vemurafenib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["BRAF mutant"]},
            {"drugs": [{"drugName": "Encorafenib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["BRAF mutant"]},
        ],
        "description": "BRAF — serine/threonine kinase in MAPK pathway.",
    },
 
    # ══════════════════════════════════════════════════════════
    # RET
    # ══════════════════════════════════════════════════════════
    ("RET", "Fusion"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Selpercatinib"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["RET fusion+ NSCLC"]},
            {"drugs": [{"drugName": "Pralsetinib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["RET fusion+ NSCLC"]},
        ],
        "description": "RET fusions — ~2% NSCLC. Selective RET inhibitors highly effective.",
    },
    ("RET", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Selpercatinib"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["RET fusion+ NSCLC"]},
            {"drugs": [{"drugName": "Pralsetinib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["RET fusion+ NSCLC"]},
            {"drugs": [{"drugName": "Cabozantinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["RET+ NSCLC"]},
        ],
        "description": "RET — fusion oncogene, ~2% NSCLC.",
    },
 
    # ══════════════════════════════════════════════════════════
    # ROS1
    # ══════════════════════════════════════════════════════════
    ("ROS1", "Fusion"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Crizotinib"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ROS1+ NSCLC"]},
            {"drugs": [{"drugName": "Lorlatinib"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ROS1+ NSCLC"]},
            {"drugs": [{"drugName": "Repotrectinib"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ROS1+ NSCLC"]},
            {"drugs": [{"drugName": "Ceritinib"}],     "level": "LEVEL_2", "pmids": [], "approvedIndications": ["ROS1+ NSCLC"]},
            {"drugs": [{"drugName": "Entrectinib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ROS1+ NSCLC"]},
        ],
        "description": "ROS1 fusions — ~2% NSCLC. Highly sensitive to ROS1/ALK inhibitors.",
    },
    ("ROS1", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Crizotinib"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ROS1+ NSCLC"]},
            {"drugs": [{"drugName": "Lorlatinib"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ROS1+ NSCLC"]},
            {"drugs": [{"drugName": "Repotrectinib"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ROS1+ NSCLC"]},
            {"drugs": [{"drugName": "Entrectinib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ROS1+ NSCLC"]},
        ],
        "description": "ROS1 — fusion oncogene, ~2% NSCLC.",
    },
 
    # ══════════════════════════════════════════════════════════
    # NTRK1/2/3
    # ══════════════════════════════════════════════════════════
    ("NTRK1", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Larotrectinib"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NTRK fusion+ solid tumors"]},
            {"drugs": [{"drugName": "Entrectinib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NTRK fusion+ solid tumors"]},
            {"drugs": [{"drugName": "Repotrectinib"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NTRK fusion+ solid tumors"]},
        ],
        "description": "NTRK1 fusion — tumor-agnostic TRK inhibitor approval.",
    },
    ("NTRK2", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Larotrectinib"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NTRK fusion+ solid tumors"]},
            {"drugs": [{"drugName": "Entrectinib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NTRK fusion+ solid tumors"]},
        ],
        "description": "NTRK2 fusion — TRK inhibitor coverage.",
    },
    ("NTRK3", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Larotrectinib"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NTRK fusion+ solid tumors"]},
            {"drugs": [{"drugName": "Entrectinib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NTRK fusion+ solid tumors"]},
            {"drugs": [{"drugName": "Repotrectinib"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NTRK fusion+ solid tumors"]},
        ],
        "description": "NTRK3 fusion — tumor-agnostic TRK inhibitor indication.",
    },
 
    # ══════════════════════════════════════════════════════════
    # TP53
    # ══════════════════════════════════════════════════════════
    ("TP53", "R248W"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_4",
        "treatments": [
            {"drugs": [{"drugName": "Pembrolizumab"}], "level": "LEVEL_4", "pmids": [], "approvedIndications": []},
        ],
        "description": "TP53 R248W — tumor suppressor inactivated. No direct targeted therapy.",
    },
    ("TP53", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_4",
        "treatments": [
            {"drugs": [{"drugName": "Selinexor"}],     "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
            {"drugs": [{"drugName": "Pembrolizumab"}], "level": "LEVEL_4",  "pmids": [], "approvedIndications": []},
        ],
        "description": "TP53 — tumor suppressor. Loss affects prognosis and immunotherapy response.",
    },
 
    # ══════════════════════════════════════════════════════════
    # PI3K / AKT / mTOR pathway
    # ══════════════════════════════════════════════════════════
    ("PIK3CA", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Alpelisib"}],    "level": "LEVEL_2", "pmids": [], "approvedIndications": ["PIK3CA mutant"]},
            {"drugs": [{"drugName": "Capivasertib"}], "level": "LEVEL_2", "pmids": [], "approvedIndications": ["PIK3CA mutant"]},
            {"drugs": [{"drugName": "Copanlisib"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["PI3K altered"]},
            {"drugs": [{"drugName": "Everolimus"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["mTOR pathway"]},
            {"drugs": [{"drugName": "Temsirolimus"}], "level": "LEVEL_2", "pmids": [], "approvedIndications": ["mTOR pathway"]},
        ],
        "description": "PIK3CA — PI3K catalytic subunit, activating mutations common in NSCLC.",
    },
    ("PIK3R1", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Copanlisib"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["PI3K altered"]},
            {"drugs": [{"drugName": "Alpelisib"}],    "level": "LEVEL_2", "pmids": [], "approvedIndications": ["PI3K altered"]},
            {"drugs": [{"drugName": "Everolimus"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["mTOR pathway"]},
        ],
        "description": "PIK3R1 — PI3K regulatory subunit.",
    },
    ("PTEN", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Capivasertib"}], "level": "LEVEL_2", "pmids": [], "approvedIndications": ["PTEN loss"]},
            {"drugs": [{"drugName": "Everolimus"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["mTOR pathway"]},
            {"drugs": [{"drugName": "Temsirolimus"}], "level": "LEVEL_2", "pmids": [], "approvedIndications": ["mTOR pathway"]},
        ],
        "description": "PTEN loss — PI3K/AKT hyperactivation. mTOR inhibitors relevant.",
    },
    ("AKT1", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Capivasertib"}], "level": "LEVEL_2", "pmids": [], "approvedIndications": ["AKT mutant"]},
            {"drugs": [{"drugName": "Ipatasertib"}],  "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
            {"drugs": [{"drugName": "Everolimus"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["mTOR pathway"]},
        ],
        "description": "AKT1 E17K — activating mutation, AKT inhibitor sensitive.",
    },
    ("MTOR", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Everolimus"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["mTOR mutant"]},
            {"drugs": [{"drugName": "Temsirolimus"}], "level": "LEVEL_2", "pmids": [], "approvedIndications": ["mTOR mutant"]},
        ],
        "description": "mTOR — activating mutations sensitive to rapalogs.",
    },
 
    # ══════════════════════════════════════════════════════════
    # FGFR pathway
    # ══════════════════════════════════════════════════════════
    ("FGFR1", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Erdafitinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
            {"drugs": [{"drugName": "Pemigatinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
            {"drugs": [{"drugName": "Futibatinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
        ],
        "description": "FGFR1 — amplified ~20% squamous NSCLC. Pan-FGFR inhibitors available.",
    },
    ("FGFR2", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Pemigatinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
            {"drugs": [{"drugName": "Erdafitinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
            {"drugs": [{"drugName": "Futibatinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
        ],
        "description": "FGFR2 — FGFR pathway alteration.",
    },
    ("FGFR3", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Erdafitinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
            {"drugs": [{"drugName": "Pemigatinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
            {"drugs": [{"drugName": "Futibatinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
        ],
        "description": "FGFR3 — FGFR pathway, fusion or mutation.",
    },
    ("FGFR4", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Futibatinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
            {"drugs": [{"drugName": "Erdafitinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
        ],
        "description": "FGFR4 — FGFR pathway alteration.",
    },
 
    # ══════════════════════════════════════════════════════════
    # DNA Repair
    # ══════════════════════════════════════════════════════════
    ("BRCA1", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Olaparib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["BRCA mutant"]},
            {"drugs": [{"drugName": "Rucaparib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["BRCA mutant"]},
            {"drugs": [{"drugName": "Niraparib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["BRCA mutant"]},
            {"drugs": [{"drugName": "Talazoparib"}],"level": "LEVEL_1", "pmids": [], "approvedIndications": ["BRCA mutant"]},
        ],
        "description": "BRCA1 loss — HRD phenotype. PARP inhibitors highly effective.",
    },
    ("BRCA2", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Olaparib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["BRCA mutant"]},
            {"drugs": [{"drugName": "Rucaparib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["BRCA mutant"]},
            {"drugs": [{"drugName": "Niraparib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["BRCA mutant"]},
            {"drugs": [{"drugName": "Talazoparib"}],"level": "LEVEL_1", "pmids": [], "approvedIndications": ["BRCA mutant"]},
        ],
        "description": "BRCA2 loss — HRD. PARP inhibitors effective.",
    },
    ("ATM", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Olaparib"}],    "level": "LEVEL_2", "pmids": [], "approvedIndications": ["ATM mutant"]},
            {"drugs": [{"drugName": "Durvalumab"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["ATM mutant"]},
            {"drugs": [{"drugName": "Niraparib"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["HRD"]},
        ],
        "description": "ATM loss — HRD phenotype. PARP inhibitor and immunotherapy benefit.",
    },
    ("POLE", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Pembrolizumab"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["TMB-High/MSI-H"]},
            {"drugs": [{"drugName": "Nivolumab"}],     "level": "LEVEL_1", "pmids": [], "approvedIndications": ["TMB-High"]},
            {"drugs": [{"drugName": "Ipilimumab"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
        ],
        "description": "POLE mutations → ultra-high TMB → exceptional immunotherapy response.",
    },
 
    # ══════════════════════════════════════════════════════════
    # Immune checkpoint
    # ══════════════════════════════════════════════════════════
    ("CD274", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Pembrolizumab"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["PD-L1+ NSCLC"]},
            {"drugs": [{"drugName": "Atezolizumab"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["PD-L1+ NSCLC"]},
            {"drugs": [{"drugName": "Durvalumab"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["PD-L1+ NSCLC"]},
            {"drugs": [{"drugName": "Avelumab"}],      "level": "LEVEL_1", "pmids": [], "approvedIndications": ["PD-L1+ NSCLC"]},
            {"drugs": [{"drugName": "Nivolumab"}],     "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
        ],
        "description": "CD274 (PD-L1) — immune checkpoint. Checkpoint inhibitors first line.",
    },
    ("PDCD1", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Pembrolizumab"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
            {"drugs": [{"drugName": "Nivolumab"}],      "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
            {"drugs": [{"drugName": "Cemiplimab"}],     "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
            {"drugs": [{"drugName": "Durvalumab"}],     "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
        ],
        "description": "PDCD1 (PD-1) — immune checkpoint on T-cells.",
    },
 
    # ══════════════════════════════════════════════════════════
    # Cell cycle
    # ══════════════════════════════════════════════════════════
    ("CDK4", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Palbociclib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDK4/6 amplified"]},
            {"drugs": [{"drugName": "Ribociclib"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDK4/6 amplified"]},
            {"drugs": [{"drugName": "Abemaciclib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDK4/6 amplified"]},
        ],
        "description": "CDK4 amplification — CDK4/6 inhibitor sensitive.",
    },
    ("CDK6", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Palbociclib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDK4/6 amplified"]},
            {"drugs": [{"drugName": "Ribociclib"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDK4/6 amplified"]},
            {"drugs": [{"drugName": "Abemaciclib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDK4/6 amplified"]},
        ],
        "description": "CDK6 amplification — CDK4/6 inhibitor coverage.",
    },
    ("CDKN2A", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Palbociclib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDKN2A loss"]},
            {"drugs": [{"drugName": "Abemaciclib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDKN2A loss"]},
            {"drugs": [{"drugName": "Ribociclib"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDKN2A loss"]},
        ],
        "description": "CDKN2A loss — CDK4/6 released, CDK inhibitors restore cell cycle control.",
    },
    ("CDKN2B", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Palbociclib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDK inhibitor"]},
        ],
        "description": "CDKN2B — CDK inhibitor, loss releases CDK4/6.",
    },
    ("CCND1", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Palbociclib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDK4/6 amplified"]},
            {"drugs": [{"drugName": "Ribociclib"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDK4/6 amplified"]},
            {"drugs": [{"drugName": "Abemaciclib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDK4/6 amplified"]},
        ],
        "description": "CCND1 (Cyclin D1) — CDK4/6 activator, amplification drives cell cycle.",
    },
 
    # ══════════════════════════════════════════════════════════
    # MAPK / HER2 / Other
    # ══════════════════════════════════════════════════════════
    ("MAP2K1", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Trametinib"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["MEK mutant"]},
            {"drugs": [{"drugName": "Cobimetinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["MEK mutant"]},
            {"drugs": [{"drugName": "Selumetinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["MEK mutant"]},
            {"drugs": [{"drugName": "Binimetinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["MEK mutant"]},
        ],
        "description": "MAP2K1 (MEK1) mutations — MEK inhibitor sensitive.",
    },
    ("MAP2K2", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Cobimetinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["MEK mutant"]},
            {"drugs": [{"drugName": "Binimetinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["MEK mutant"]},
            {"drugs": [{"drugName": "Trametinib"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["MEK mutant"]},
        ],
        "description": "MAP2K2 (MEK2) — MAPK cascade.",
    },
    ("NF1", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Trametinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["NF1 loss"]},
            {"drugs": [{"drugName": "Cobimetinib"}], "level": "LEVEL_2", "pmids": [], "approvedIndications": ["NF1 loss"]},
            {"drugs": [{"drugName": "Everolimus"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["NF1 loss"]},
        ],
        "description": "NF1 loss — RAS hyperactivation. MEK + mTOR inhibitors relevant.",
    },
    ("ERBB2", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Trastuzumab Deruxtecan"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["HER2 mutant NSCLC"]},
            {"drugs": [{"drugName": "Neratinib"}],              "level": "LEVEL_2", "pmids": [], "approvedIndications": ["HER2 mutant"]},
            {"drugs": [{"drugName": "Afatinib"}],               "level": "LEVEL_2", "pmids": [], "approvedIndications": ["HER2 mutant NSCLC"]},
        ],
        "description": "ERBB2 (HER2) — ~3% NSCLC. T-DXd FDA approved 2022.",
    },
    ("MDM2", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_3A",
        "treatments": [
            {"drugs": [{"drugName": "Idasanutlin"}],     "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
            {"drugs": [{"drugName": "Pembrolizumab"}],   "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
        ],
        "description": "MDM2 amplification degrades TP53. MDM2 inhibitors restore p53 function.",
    },
    ("STK11", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_3A",
        "treatments": [
            {"drugs": [{"drugName": "Everolimus"}],     "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
            {"drugs": [{"drugName": "Pembrolizumab"}],  "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
        ],
        "description": "STK11 loss — immunotherapy resistance marker. mTOR pathway activated.",
    },
    ("KEAP1", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_3A",
        "treatments": [
            {"drugs": [{"drugName": "Osimertinib"}],   "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
            {"drugs": [{"drugName": "Pembrolizumab"}], "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
        ],
        "description": "KEAP1 loss — poor prognosis, resistance to EGFR TKI and immunotherapy.",
    },
    ("ARID1A", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_3A",
        "treatments": [
            {"drugs": [{"drugName": "Tazemetostat"}],  "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
            {"drugs": [{"drugName": "Niraparib"}],     "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
            {"drugs": [{"drugName": "Atezolizumab"}],  "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
        ],
        "description": "ARID1A — SWI/SNF complex, tumor suppressor.",
    },
    ("SMARCA4", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_3A",
        "treatments": [
            {"drugs": [{"drugName": "Tazemetostat"}],  "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
            {"drugs": [{"drugName": "Abemaciclib"}],   "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
        ],
        "description": "SMARCA4 — SWI/SNF chromatin remodeling complex.",
    },
    ("RAF1", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Trametinib"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["RAF1 altered"]},
            {"drugs": [{"drugName": "Cobimetinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["RAF1 altered"]},
            {"drugs": [{"drugName": "Encorafenib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["RAF altered"]},
        ],
        "description": "RAF1 — MAPK pathway kinase.",
    },
    ("RB1", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Palbociclib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["cell cycle"]},
            {"drugs": [{"drugName": "Ribociclib"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["cell cycle"]},
        ],
        "description": "RB1 — cell cycle brake. Loss releases CDK4/6 activity.",
    },
    ("MYC", "any"): {
        "oncogenicity": "Oncogenic", "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_3A",
        "treatments": [
            {"drugs": [{"drugName": "Pembrolizumab"}],  "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
        ],
        "description": "MYC amplification — no direct approved targeted therapy. Immunotherapy may help.",
    },
}
}

LEVEL_COLORS = {
    "LEVEL_1": "#27500A",   # FDA-approved
    "LEVEL_2": "#0C447C",   # Standard care
    "LEVEL_3A": "#633806",  # Clinical evidence
    "LEVEL_3B": "#633806",
    "LEVEL_4": "#5F5E5A",   # Biological evidence
    "LEVEL_R1": "#791F1F",  # Resistance
}

LEVEL_LABELS = {
    "LEVEL_1":  "FDA Approved",
    "LEVEL_2":  "Standard of Care",
    "LEVEL_3A": "Clinical Evidence",
    "LEVEL_3B": "Clinical Evidence",
    "LEVEL_4":  "Biological Evidence",
    "LEVEL_R1": "Resistance",
}


def query_oncokb(gene: str, alteration: str,
                 tumor_type: str = "NSCLC") -> dict:
    if ONCOKB_TOKEN != "YOUR_TOKEN_HERE":
        endpoint = f"{BASE_URL}/annotate/mutations/byProteinChange"
        params = {
            "hugoSymbol": gene,
            "alteration": alteration,
            "tumorType": tumor_type,
            "evidenceType": "ONCOGENIC,TREATMENTS",
        }
        try:
            resp = requests.get(endpoint, headers=HEADERS,
                                params=params, timeout=10)
            if resp.status_code == 200:
                return _parse_oncokb_response(resp.json())
        except requests.RequestException:
            pass
    return _local_lookup(gene, alteration)


def _parse_oncokb_response(data: dict) -> dict:
    treatments = []
    for tx in data.get("treatments", []):
        treatments.append({
            "drugs": tx.get("drugs", []),
            "level": tx.get("level", ""),
            "pmids": tx.get("pmids", []),
            "approvedIndications": tx.get("approvedIndications", []),
        })
    return {
        "oncogenicity": data.get("oncogenic", "Unknown"),
        "mutationEffect": data.get("mutationEffect", {}).get("knownEffect", "Unknown"),
        "highestSensitiveLevel": data.get("highestSensitiveLevel", ""),
        "treatments": treatments,
        "description": data.get("mutationEffect", {}).get("description", ""),
    }

def _local_lookup(gene: str, alteration: str) -> dict:
    gene = gene.upper()
    # 1. ลองหา exact match ก่อน
    key = (gene, alteration)
    if key in LOCAL_DB:
        return LOCAL_DB[key]
    # 2. ลอง "any" key สำหรับ gene ที่ไม่ได้ระบุ alteration
    key_any = (gene, "any")
    if key_any in LOCAL_DB:
        return LOCAL_DB[key_any]
    # 3. ไม่พบ
    return {
        "oncogenicity": "Unknown",
        "mutationEffect": "Unknown",
        "highestSensitiveLevel": "",
        "treatments": [],
        "description": f"No curated data for {gene} {alteration}. "
                       "Consider checking ClinVar or COSMIC manually.",
    }

def query_all_mutations(mutation_list: list[dict]) -> list[dict]:
    """
    Input:  [{"gene": "EGFR", "alteration": "L858R", "vaf": 0.42}, ...]
    Output: same list + oncokb_data field เพิ่ม
    """
    results = []
    for mut in mutation_list:
        gene = mut.get("gene", "")
        alteration = mut.get("alteration", "")
        info = query_oncokb(gene, alteration)
        results.append({**mut, "oncokb": info})
    return results
