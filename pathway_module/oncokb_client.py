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
    ("AKT1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "CAPIVASERTIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "NELFINAVIR"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "NINTEDANIB ESYLATE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TOPOTECAN HYDROCHLORIDE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "EVEROLIMUS"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "AKT1 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("ALK", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "ALECTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "LORLATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "BRIGATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CRIZOTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CERITINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "ALK — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("ARID1A", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "TAZEMETOSTAT"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "NIRAPARIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ATEZOLIZUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TALAZOPARIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "NIVOLUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "ARID1A — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("ATM", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "BENDAMUSTINE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "OLAPARIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "DURVALUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "AVELUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "RUCAPARIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "ATM — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("BRAF", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "DABRAFENIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "VEMURAFENIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "PANITUMUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TRAMETINIB DIMETHYL SULFOXIDE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ENCORAFENIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "BRAF — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("BRCA1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "RUCAPARIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "NIRAPARIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "OLAPARIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TALAZOPARIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "BLEOMYCIN"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "BRCA1 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("BRCA2", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "RUCAPARIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "OLAPARIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "NIRAPARIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TALAZOPARIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ENZALUTAMIDE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "BRCA2 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("CCND1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "URACIL"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "RIBOCICLIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "PALBOCICLIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "BEXAROTENE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "LAPATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "CCND1 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("CD274", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "PEMBROLIZUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "AVELUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ATEZOLIZUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "DURVALUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "NIVOLUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "CD274 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("CDK4", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "RIBOCICLIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ABEMACICLIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "PALBOCICLIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CAMPTOTHECIN"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "DEXAMETHASONE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "CDK4 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("CDK6", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "RIBOCICLIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ABEMACICLIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "PALBOCICLIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "FULVESTRANT"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "DEXAMETHASONE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "CDK6 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("CDKN2A", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "PALBOCICLIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ABEMACICLIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "RIBOCICLIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "DABRAFENIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TRAMETINIB DIMETHYL SULFOXIDE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "CDKN2A — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("CDKN2B", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "PALBOCICLIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "CDKN2B — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("EGFR", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "AFATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "MOBOCERTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "NECITUMUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CETUXIMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "DACOMITINIB ANHYDROUS"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "EGFR — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("ERBB2", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "NERATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "DACOMITINIB ANHYDROUS"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "MARGETUXIMAB-CMKB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "LAPATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "FAM-TRASTUZUMAB DERUXTECAN-NXKI"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "ERBB2 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("FGFR1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "PEMIGATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ERDAFITINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "FUTIBATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "INFIGRATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "NINTEDANIB ESYLATE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "FGFR1 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("FGFR2", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "PEMIGATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ERDAFITINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "FUTIBATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "INFIGRATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "PONATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "FGFR2 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("FGFR3", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "ERDAFITINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "PEMIGATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "INFIGRATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "FUTIBATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "NINTEDANIB ESYLATE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "FGFR3 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("FGFR4", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "FUTIBATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ERDAFITINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "NINTEDANIB ESYLATE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "INFIGRATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "EVEROLIMUS"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "FGFR4 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("KEAP1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "OSIMERTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CERITINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "AFATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CRIZOTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "PEMBROLIZUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "KEAP1 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("KRAS", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "PANITUMUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ADAGRASIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CETUXIMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "SOTORASIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TEPROTUMUMAB-TRBW"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "KRAS — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("MAP2K1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "COBIMETINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TRAMETINIB DIMETHYL SULFOXIDE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "SELUMETINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "BINIMETINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "VEMURAFENIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "MAP2K1 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("MAP2K2", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "COBIMETINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "BINIMETINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "SELUMETINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TRAMETINIB DIMETHYL SULFOXIDE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "DABRAFENIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "MAP2K2 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("MDM2", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "PEMBROLIZUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "NIVOLUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ATEZOLIZUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TOPOTECAN HYDROCHLORIDE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CRIZOTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "MDM2 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("MET", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "CAPMATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TEPOTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CRIZOTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CABOZANTINIB S-MALATE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "AMIVANTAMAB-VMJW"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "MET — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("MTOR", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "TEMSIROLIMUS"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "EVEROLIMUS"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "GLASDEGIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "SIROLIMUS"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "SAPANISERTIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "MTOR — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("MYC", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "SULINDAC"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "THIOGUANINE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TEMOZOLOMIDE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "AZACITIDINE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "VERAPAMIL"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "MYC — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("NF1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "EVEROLIMUS"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TRAMETINIB DIMETHYL SULFOXIDE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "VEMURAFENIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "COBIMETINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "BINIMETINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "NF1 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("NTRK1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "LAROTRECTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "REPOTRECTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ENTRECTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CRIZOTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "REGORAFENIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "NTRK1 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("NTRK2", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "LAROTRECTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ENTRECTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CRIZOTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CISPLATIN"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "DOXORUBICIN HYDROCHLORIDE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "NTRK2 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("NTRK3", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "LAROTRECTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ENTRECTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "REPOTRECTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "MIDOSTAURIN"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CRIZOTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "NTRK3 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("PDCD1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "CEMIPLIMAB-RWLC"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "NIVOLUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "DURVALUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "PEMBROLIZUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "PDCD1 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("PIK3CA", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "ALPELISIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CAPIVASERTIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TEMSIROLIMUS"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "COPANLISIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "EVEROLIMUS"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "PIK3CA — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("PIK3R1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "COPANLISIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ALPELISIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "EVEROLIMUS"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "INFIGRATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "QUERCETIN"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "PIK3R1 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("POLE", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "PEMBROLIZUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "NIVOLUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CLOFARABINE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "IPILIMUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "FLUDARABINE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "POLE — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("PTEN", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "CAPMATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CAPIVASERTIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TEMSIROLIMUS"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ENZALUTAMIDE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "EVEROLIMUS"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "PTEN — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("RAF1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "ENCORAFENIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "COBIMETINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "REGORAFENIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "SORAFENIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "DOCETAXEL ANHYDROUS"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "RAF1 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("RB1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "FOSTAMATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "RIBOCICLIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "PALBOCICLIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "LORLATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "LETROZOLE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "RB1 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("RET", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "SELPERCATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "PRALSETINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CABOZANTINIB S-MALATE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "VANDETANIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "SUNITINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "RET — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("ROS1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "CRIZOTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "LORLATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "REPOTRECTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CERITINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "BRIGATINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "ROS1 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("SMARCA4", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "TAZEMETOSTAT"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "RIBOCICLIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ABEMACICLIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "VINORELBINE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TRETINOIN"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "SMARCA4 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("STK11", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "PHENFORMIN"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "EVEROLIMUS"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "AVELUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "CAPIVASERTIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "EXEMESTANE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "STK11 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    ("TP53", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "BENDAMUSTINE"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ALECTINIB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "SELINEXOR"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "ALEMTUZUMAB"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
            {"drugs": [{"drugName": "TRABECTEDIN"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ['NSCLC']},
        ],
        "description": "TP53 — drug interactions from DGIdb (anti-neoplastic, lung cancer relevant)",
    },
    # เพิ่มใน LOCAL_DB dict ใน oncokb_client.py

    # ── RTK Fusions ──────────────────────────────────────────
    ("ROS1", "Fusion"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Crizotinib"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ROS1+ NSCLC"]},
            {"drugs": [{"drugName": "Lorlatinib"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ROS1+ NSCLC"]},
            {"drugs": [{"drugName": "Repotrectinib"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["ROS1+ NSCLC"]},
        ],
        "description": "ROS1 fusions in ~2% NSCLC. Highly sensitive to ROS1 inhibitors.",
    },
    ("RET", "Fusion"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Selpercatinib"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["RET fusion+ NSCLC"]},
            {"drugs": [{"drugName": "Pralsetinib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["RET fusion+ NSCLC"]},
        ],
        "description": "RET fusions in ~2% NSCLC. Selective RET inhibitors highly effective.",
    },
    ("NTRK1", "Fusion"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Larotrectinib"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NTRK fusion+ solid tumors"]},
            {"drugs": [{"drugName": "Entrectinib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NTRK fusion+ solid tumors"]},
        ],
        "description": "NTRK fusions — tumor-agnostic approval for TRK inhibitors.",
    },
    ("NTRK2", "Fusion"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Larotrectinib"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NTRK fusion+ solid tumors"]},
            {"drugs": [{"drugName": "Entrectinib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NTRK fusion+ solid tumors"]},
        ],
        "description": "NTRK2 fusion — same TRK inhibitor coverage as NTRK1.",
    },
    ("NTRK3", "Fusion"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Larotrectinib"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NTRK fusion+ solid tumors"]},
            {"drugs": [{"drugName": "Entrectinib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NTRK fusion+ solid tumors"]},
        ],
        "description": "NTRK3 fusion — tumor-agnostic TRK inhibitor indication.",
    },

    # ── PI3K/AKT/mTOR pathway ────────────────────────────────
    ("PIK3CA", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Alpelisib"}],    "level": "LEVEL_2", "pmids": [], "approvedIndications": ["PIK3CA mutant"]},
            {"drugs": [{"drugName": "Capivasertib"}], "level": "LEVEL_2", "pmids": [], "approvedIndications": ["PIK3CA mutant"]},
            {"drugs": [{"drugName": "Everolimus"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["mTOR pathway"]},
        ],
        "description": "PIK3CA mutations activate PI3K/AKT/mTOR survival pathway.",
    },
    ("PTEN", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Capivasertib"}], "level": "LEVEL_2", "pmids": [], "approvedIndications": ["PTEN loss"]},
            {"drugs": [{"drugName": "Everolimus"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["mTOR pathway"]},
        ],
        "description": "PTEN loss activates PI3K/AKT. Sensitizes to AKT/mTOR inhibitors.",
    },
    ("MTOR", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Everolimus"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["mTOR mutant"]},
            {"drugs": [{"drugName": "Temsirolimus"}], "level": "LEVEL_2", "pmids": [], "approvedIndications": ["mTOR mutant"]},
        ],
        "description": "mTOR activating mutations — rapalog sensitivity.",
    },
    ("AKT1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Capivasertib"}], "level": "LEVEL_2", "pmids": [], "approvedIndications": ["AKT1 mutant"]},
            {"drugs": [{"drugName": "Ipatasertib"}],  "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
        ],
        "description": "AKT1 E17K — activating mutation, AKT inhibitor sensitive.",
    },

    # ── FGFR pathway ─────────────────────────────────────────
    ("FGFR1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Erdafitinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
            {"drugs": [{"drugName": "Pemigatinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
            {"drugs": [{"drugName": "Futibatinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
        ],
        "description": "FGFR1 amplification common in squamous cell lung cancer (~20%).",
    },
    ("FGFR2", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Pemigatinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
            {"drugs": [{"drugName": "Erdafitinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
        ],
        "description": "FGFR2 fusions/mutations — pan-FGFR inhibitor coverage.",
    },
    ("FGFR3", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Erdafitinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["FGFR altered"]},
            {"drugs": [{"drugName": "Infigratinib"}], "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
        ],
        "description": "FGFR3 mutations/fusions — FGFR inhibitor sensitive.",
    },

    # ── DNA Repair ───────────────────────────────────────────
    ("BRCA2", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Olaparib"}],   "level": "LEVEL_1", "pmids": [], "approvedIndications": ["BRCA mutant"]},
            {"drugs": [{"drugName": "Rucaparib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["BRCA mutant"]},
            {"drugs": [{"drugName": "Niraparib"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["BRCA mutant"]},
        ],
        "description": "BRCA2 loss causes HRD — PARP inhibitors highly effective.",
    },
    ("ATM", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Olaparib"}],    "level": "LEVEL_2", "pmids": [], "approvedIndications": ["ATM mutant"]},
            {"drugs": [{"drugName": "Durvalumab"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["ATM mutant"]},
        ],
        "description": "ATM loss — HRD phenotype, PARP inhibitor and immunotherapy benefit.",
    },
    ("POLE", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Pembrolizumab"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["TMB-High/MSI-H"]},
            {"drugs": [{"drugName": "Nivolumab"}],     "level": "LEVEL_1", "pmids": [], "approvedIndications": ["TMB-High"]},
        ],
        "description": "POLE mutations → ultra-high TMB → exceptional immunotherapy response.",
    },

    # ── Immune checkpoint ────────────────────────────────────
    ("CD274", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Pembrolizumab"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["PD-L1+ NSCLC"]},
            {"drugs": [{"drugName": "Atezolizumab"}],  "level": "LEVEL_1", "pmids": [], "approvedIndications": ["PD-L1+ NSCLC"]},
            {"drugs": [{"drugName": "Durvalumab"}],    "level": "LEVEL_1", "pmids": [], "approvedIndications": ["PD-L1+ NSCLC"]},
        ],
        "description": "PD-L1 overexpression — checkpoint inhibitor first line.",
    },
    ("PDCD1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Pembrolizumab"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
            {"drugs": [{"drugName": "Nivolumab"}],     "level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
            {"drugs": [{"drugName": "Cemiplimab-Rwlc"}],"level": "LEVEL_1", "pmids": [], "approvedIndications": ["NSCLC"]},
        ],
        "description": "PD-1 pathway — checkpoint inhibitor sensitive.",
    },

    # ── Cell cycle ───────────────────────────────────────────
    ("CDK4", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Palbociclib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDK4/6 amplified"]},
            {"drugs": [{"drugName": "Ribociclib"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDK4/6 amplified"]},
            {"drugs": [{"drugName": "Abemaciclib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDK4/6 amplified"]},
        ],
        "description": "CDK4 amplification — CDK4/6 inhibitor sensitive.",
    },
    ("CDK6", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Palbociclib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDK4/6 amplified"]},
            {"drugs": [{"drugName": "Abemaciclib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDK4/6 amplified"]},
        ],
        "description": "CDK6 amplification — CDK4/6 inhibitor coverage.",
    },
    ("CDKN2A", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Palbociclib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDKN2A loss"]},
            {"drugs": [{"drugName": "Abemaciclib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["CDKN2A loss"]},
        ],
        "description": "CDKN2A loss releases CDK4/6 — CDK inhibitors restore cell cycle control.",
    },

    # ── Other MAPK ───────────────────────────────────────────
    ("MAP2K1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Trametinib"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["MEK mutant"]},
            {"drugs": [{"drugName": "Cobimetinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["MEK mutant"]},
            {"drugs": [{"drugName": "Selumetinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["MEK mutant"]},
        ],
        "description": "MAP2K1 (MEK1) mutations — MEK inhibitor sensitive.",
    },
    ("NF1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_2",
        "treatments": [
            {"drugs": [{"drugName": "Trametinib"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["NF1 loss"]},
            {"drugs": [{"drugName": "Everolimus"}],  "level": "LEVEL_2", "pmids": [], "approvedIndications": ["NF1 loss"]},
        ],
        "description": "NF1 loss activates RAS — MEK inhibitors and mTOR inhibitors relevant.",
    },
    ("ERBB2", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_1",
        "treatments": [
            {"drugs": [{"drugName": "Trastuzumab Deruxtecan"}], "level": "LEVEL_1", "pmids": [], "approvedIndications": ["HER2 mutant NSCLC"]},
            {"drugs": [{"drugName": "Neratinib"}],   "level": "LEVEL_2", "pmids": [], "approvedIndications": ["HER2 mutant"]},
            {"drugs": [{"drugName": "Afatinib"}],    "level": "LEVEL_2", "pmids": [], "approvedIndications": ["HER2 mutant NSCLC"]},
        ],
        "description": "ERBB2 (HER2) mutations in ~3% NSCLC — T-DXd now FDA approved.",
    },
    ("STK11", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_3A",
        "treatments": [
            {"drugs": [{"drugName": "Everolimus"}],      "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
            {"drugs": [{"drugName": "Pembrolizumab"}],   "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
        ],
        "description": "STK11 loss — associated with immunotherapy resistance. mTOR pathway activated.",
    },
    ("KEAP1", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Loss-of-function",
        "highestSensitiveLevel": "LEVEL_3A",
        "treatments": [
            {"drugs": [{"drugName": "Osimertinib"}],   "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
        ],
        "description": "KEAP1 mutations — associated with poor prognosis and resistance to EGFR TKI.",
    },
    ("MDM2", "any"): {
        "oncogenicity": "Oncogenic",
        "mutationEffect": "Gain-of-function",
        "highestSensitiveLevel": "LEVEL_3A",
        "treatments": [
            {"drugs": [{"drugName": "Idasanutlin"}],     "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
            {"drugs": [{"drugName": "Pembrolizumab"}],   "level": "LEVEL_3A", "pmids": [], "approvedIndications": []},
        ],
        "description": "MDM2 amplification degrades TP53 — MDM2 inhibitors restore p53 function.",
    },
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


def query_oncokb(gene: str, alteration: str, tumor_type: str = "NSCLC") -> dict:
    """
    Query OncoKB API สำหรับ 1 mutation
    ถ้า token ไม่ valid จะ fallback ไป local DB อัตโนมัติ
    """
    if ONCOKB_TOKEN == "YOUR_TOKEN_HERE":
        return _local_lookup(gene, alteration)

    endpoint = f"{BASE_URL}/annotate/mutations/byProteinChange"
    params = {
        "hugoSymbol": gene,
        "alteration": alteration,
        "tumorType": tumor_type,
        "evidenceType": "ONCOGENIC,TREATMENTS",
    }

    try:
        resp = requests.get(endpoint, headers=HEADERS, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return _parse_oncokb_response(data)
        else:
            return _local_lookup(gene, alteration)
    except requests.RequestException:
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
