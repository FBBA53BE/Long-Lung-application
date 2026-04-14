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
    key = (gene.upper(), alteration)
    if key in LOCAL_DB:
        return LOCAL_DB[key]
    # Generic fallback
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
