import streamlit as st
import tensorflow as tf
import numpy as np
import gdown
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from PIL import Image
import time
import pandas as pd
import io

import torch
import torch.nn as nn
import segmentation_models_pytorch as smp
# ════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Long Lung",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ════════════════════════════════════════════════════════════
# CUSTOM CSS
# ════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:ital,wght@0,300;0,400;1,300&display=swap');

:root {
    --bg:        #050A0E;
    --surface:   #0D1B24;
    --card:      #112030;
    --accent:    #00C8A0;
    --accent2:   #0077FF;
    --danger:    #FF4D6D;
    --text:      #E8F4F0;
    --muted:     #5A7A70;
    --border:    rgba(0,200,160,0.15);
}

* { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(0,200,160,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(0,119,255,0.06) 0%, transparent 60%),
        var(--bg) !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 2rem 4rem !important; max-width: 1200px; margin: auto; }

/* ── HERO ── */
.hero {
    text-align: center;
    padding: 5rem 2rem 3rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem;
    font-weight: 300;
    letter-spacing: 0.3em;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(3.5rem, 8vw, 7rem);
    font-weight: 800;
    line-height: 0.95;
    letter-spacing: -0.03em;
    margin: 0 0 1.2rem;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent) 60%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-tagline {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.1rem;
    font-weight: 300;
    font-style: italic;
    color: var(--muted);
    letter-spacing: 0.05em;
    margin-bottom: 3rem;
}
.hero-divider {
    width: 60px;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    margin: 0 auto 3rem;
    border-radius: 2px;
}

/* ── UPLOAD ZONE ── */
.upload-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    text-align: center;
    display: block;
    margin-bottom: 0.75rem;
}
[data-testid="stFileUploader"] {
    background: var(--card) !important;
    border: 1.5px dashed var(--accent) !important;
    border-radius: 20px !important;
    padding: 2.5rem !important;
    transition: all 0.3s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent2) !important;
    background: rgba(0,200,160,0.04) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] { color: var(--muted) !important; }

/* ── CARDS ── */
.result-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 1.8rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.result-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 1rem;
}

/* ── PREDICTION BADGE ── */
.pred-cancer {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--danger);
}
.pred-normal {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--accent);
}
.pred-benign {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #FFB347;
}
.conf-text {
    font-size: 0.9rem;
    color: var(--muted);
    margin-top: 0.3rem;
}

/* ── PROCESSING ── */
.processing-box {
    text-align: center;
    padding: 3rem;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    margin: 2rem 0;
}
.processing-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--accent);
    margin-top: 1rem;
    letter-spacing: 0.1em;
}
.processing-sub {
    font-size: 0.85rem;
    color: var(--muted);
    margin-top: 0.5rem;
}

/* ── SECTION HEADER ── */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--accent);
    margin: 2.5rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── CONFIDENCE BAR ── */
.conf-bar-wrap { margin: 0.4rem 0; }
.conf-bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.78rem;
    color: var(--muted);
    margin-bottom: 0.2rem;
}
.conf-bar-track {
    height: 6px;
    background: rgba(255,255,255,0.05);
    border-radius: 99px;
    overflow: hidden;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.8s ease;
}

/* ── FOOTER ── */
.footer {
    text-align: center;
    padding: 3rem 0 1rem;
    font-size: 0.75rem;
    color: var(--muted);
    letter-spacing: 0.05em;
}

/* ── STREAMLIT OVERRIDES ── */
h1,h2,h3 { font-family: 'Syne', sans-serif !important; }
[data-testid="stSpinner"] > div { border-top-color: var(--accent) !important; }
.stImage img { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# CONSTANTS
# ════════════════════════════════════════════════════════════
USE_CLASSES = [
    "Adenocarcinoma",
    "Benign",
    "Large cell carcinoma",
    "Normal",
    "Squamous cell carcinoma",
]
CANCER_CLASSES = ["Adenocarcinoma", "Large cell carcinoma", "Squamous cell carcinoma"]

BAR_COLORS = {
    "Adenocarcinoma":        "#FF4D6D",
    "Benign":                "#FFB347",
    "Large cell carcinoma":  "#FF4D6D",
    "Normal":                "#00C8A0",
    "Squamous cell carcinoma": "#FF4D6D",
}





# ════════════════════════════════════════════════════════════
# MODEL LOADING
# ════════════════════════════════════════════════════════════

@st.cache_resource
def load_models():
    # ── EfficientNet (.keras) ──
    if not os.path.exists("EffnetModel.keras"):
        with st.spinner("Downloading classification model…"):
            gdown.download(
                "https://drive.google.com/file/d/1I3uHydg5JDTi6EQ1xn9ZQ1daDcXb9csW/view?usp=share_link",  # ← แก้ตรงนี้
                "EffnetModel.keras", quiet=False
            )
    effnet = tf.keras.models.load_model("EffnetModel.keras")

    # ── U-Net (.pth — PyTorch, smp.Unet + resnet34) ──
    if not os.path.exists("unet_lung_cancer_full_NEW.pth"):
        with st.spinner("Downloading segmentation model…"):
            gdown.download(
                "https://drive.google.com/file/d/1tPo-cywtiLAJAEOVORoiomSuNV7g40FV/view?usp=share_link",
                "unet_lung_cancer_full_NEW.pth", quiet=False
            )
    # Checkpoint is a dict — rebuild architecture then load weights
    ckpt = torch.load("unet_lung_cancer_full_NEW.pth",
                      map_location=torch.device("cpu"),
                      weights_only=False)
    encoder   = ckpt.get("encoder",   "resnet34")
    img_size  = ckpt.get("img_size",  256)
    threshold = ckpt.get("threshold", 0.5)

    unet = smp.Unet(
        encoder_name=encoder,
        encoder_weights=None,          # weights come from the checkpoint
        in_channels=3,
        classes=1,
        activation=None,
        decoder_attention_type="scse",
    )
    unet.load_state_dict(ckpt["model_state_dict"])
    unet.eval()

    return effnet, unet, img_size, threshold

effnet_model, unet_model, UNET_IMG_SIZE, UNET_THRESHOLD = load_models()
# ════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════
def preprocess(img: Image.Image):
    img = img.convert("RGB").resize((224, 224))
    arr = np.array(img, dtype=np.float32) / 255.0
    return img, np.expand_dims(arr, 0)

def classify(arr, model):
    probs      = model.predict(arr, verbose=0)[0]
    pred_idx   = np.argmax(probs)
    return USE_CLASSES[pred_idx], float(probs[pred_idx]) * 100, probs

def make_gradcam(img_array, model):
    try:
        effnet     = model.get_layer("efficientnetb0")
        conv_layer = effnet.get_layer("top_conv")
        grad_model = tf.keras.models.Model(
            inputs=effnet.input,
            outputs=[conv_layer.output, effnet.output]
        )
        with tf.GradientTape() as tape:
            conv_outputs, effnet_out = grad_model(img_array)
            x           = model.get_layer("global_average_pooling2d")(effnet_out)
            x           = model.get_layer("dense")(x)
            x           = model.get_layer("dropout")(x, training=False)
            predictions = model.get_layer("dense_1")(x)
            pred_idx    = tf.argmax(predictions[0])
            pred_score  = predictions[:, pred_idx]
        grads   = tape.gradient(pred_score, conv_outputs)
        pooled  = tf.reduce_mean(grads, axis=(0, 1, 2))
        heatmap = conv_outputs[0] @ pooled[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
        return heatmap.numpy()
    except Exception:
        return None

def overlay_gradcam(img: Image.Image, heatmap, alpha=0.45):
    h = np.array(Image.fromarray(np.uint8(heatmap * 255)).resize((224, 224))) / 255.0
    colored = cm.get_cmap("jet")(h)[..., :3]
    base    = np.array(img, dtype=np.float32) / 255.0
    return np.clip((1 - alpha) * base + alpha * colored, 0, 1)

def segment_unet(img: Image.Image, unet):
    size = UNET_IMG_SIZE  # 256 from checkpoint
    arr  = np.array(img.resize((size, size)), dtype=np.float32)

    # Normalise same as training (per-image min-max)
    arr = arr - arr.min()
    if arr.max() > 0:
        arr = arr / arr.max()

    # (H,W,3) → (1,3,H,W)
    tensor = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).float()

    with torch.no_grad():
        logit = unet(tensor)                      # raw logits (1,1,H,W)
        mask  = torch.sigmoid(logit)[0, 0].numpy()

    return (mask > UNET_THRESHOLD).astype(np.float32)

def overlay_mask(img: Image.Image, mask):
    base     = np.array(img.resize((256, 256)), dtype=np.float32) / 255.0
    red      = np.zeros_like(base)
    red[..., 0] = mask
    return np.clip(base + 0.45 * red, 0, 1)

def conf_bars_html(probs):
    html = ""
    for cls, p in sorted(zip(USE_CLASSES, probs), key=lambda x: -x[1]):
        pct   = p * 100
        color = BAR_COLORS.get(cls, "#00C8A0")
        html += f"""
        <div class="conf-bar-wrap">
            <div class="conf-bar-label">
                <span>{cls}</span><span>{pct:.1f}%</span>
            </div>
            <div class="conf-bar-track">
                <div class="conf-bar-fill" style="width:{pct}%; background:{color};"></div>
            </div>
        </div>"""
    return html

# ════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">AI-Powered Pulmonary Analysis</div>
    <div class="hero-title">Long Lung</div>
    <div class="hero-tagline">Faster Detect &nbsp;·&nbsp; Longer Our Lungs</div>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# UPLOAD
# ════════════════════════════════════════════════════════════
st.markdown('<span class="upload-label">Upload your CT-scan here</span>', unsafe_allow_html=True)
uploaded = st.file_uploader(
    label="",
    type=["png", "jpg", "jpeg"],
    label_visibility="collapsed"
)

# ════════════════════════════════════════════════════════════
# MAIN FLOW
# ════════════════════════════════════════════════════════════
if uploaded:

    # ── Processing animation ──
    proc = st.empty()
    proc.markdown("""
    <div class="processing-box">
        <div style="font-size:3rem;">⏳</div>
        <div class="processing-title">PROCESSING</div>
        <div class="processing-sub">Running inference on your CT scan…</div>
    </div>
    """, unsafe_allow_html=True)

    img = Image.open(uploaded)
    img_resized, arr = preprocess(img)

    # ── Step 1: Classify ──
    pred_class, confidence, probs = classify(arr, effnet_model)

    # ── Step 2: Grad-CAM ──
    heatmap = make_gradcam(arr, effnet_model)
    overlay = overlay_gradcam(img_resized, heatmap) if heatmap is not None else None

    # ── Step 3: U-Net (if cancer & model loaded) ──
    seg_overlay = None
    if pred_class in CANCER_CLASSES and unet_model is not None:
        mask        = segment_unet(img_resized, unet_model)
        seg_overlay = overlay_mask(img_resized, mask)

    proc.empty()  # ลบ processing box

    # ════════════════════════════════════════════
    # RESULTS LAYOUT
    # ════════════════════════════════════════════
    st.markdown('<div class="section-header">Analysis Results</div>', unsafe_allow_html=True)

    col_img, col_result = st.columns([1, 1.2], gap="large")

    with col_img:
        st.markdown('<div class="result-card"><div class="card-title">CT Scan Input</div>', unsafe_allow_html=True)
        st.image(img_resized, use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_result:
        # Prediction
        is_cancer = pred_class in CANCER_CLASSES
        cls_class = "pred-cancer" if is_cancer else ("pred-normal" if pred_class == "Normal" else "pred-benign")
        icon      = "🔴" if is_cancer else "🟢"

        st.markdown(f"""
        <div class="result-card">
            <div class="card-title">Prediction</div>
            <div class="{cls_class}">{icon} {pred_class}</div>
            <div class="conf-text">Confidence: <strong style="color:white">{confidence:.1f}%</strong></div>
            <br>
            {conf_bars_html(probs)}
        </div>
        """, unsafe_allow_html=True)

    # ── Grad-CAM ──
    if overlay is not None:
        st.markdown('<div class="section-header">Grad-CAM Heatmap</div>', unsafe_allow_html=True)
        gc1, gc2 = st.columns(2, gap="large")
        with gc1:
            st.markdown('<div class="result-card"><div class="card-title">Original</div>', unsafe_allow_html=True)
            st.image(img_resized, use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with gc2:
            st.markdown('<div class="result-card"><div class="card-title">Region of Interest</div>', unsafe_allow_html=True)
            st.image(overlay, use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Segmentation ──
    if seg_overlay is not None:
        st.markdown('<div class="section-header">Tumor Segmentation</div>', unsafe_allow_html=True)
        s1, s2 = st.columns(2, gap="large")
        with s1:
            st.markdown('<div class="result-card"><div class="card-title">Original</div>', unsafe_allow_html=True)
            st.image(img_resized, use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with s2:
            st.markdown('<div class="result-card"><div class="card-title">Tumor Region</div>', unsafe_allow_html=True)
            st.image(seg_overlay, use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    elif pred_class in CANCER_CLASSES and unet_model is None:
        st.info("🔬 Segmentation model not loaded yet — coming soon.")
    elif pred_class not in CANCER_CLASSES:
        st.markdown("""
        <div class="result-card" style="text-align:center; padding: 2rem;">
            <div style="font-size:2.5rem;">✅</div>
            <div class="card-title" style="margin-top:0.5rem;">No malignant tumor detected</div>
            <div style="color:var(--muted); font-size:0.9rem;">Segmentation not required for this case.</div>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TSV → CSV CONVERTER  (Mutation file: Gene / Protein Change / Allele Freq)
# ════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">Mutation TSV → CSV Converter</div>', unsafe_allow_html=True)

with st.expander("Upload a patient mutation .tsv file to convert it to .csv", expanded=False):
    tsv_file = st.file_uploader(
        label="",
        type=["tsv", "txt"],
        key="tsv_uploader",
        label_visibility="collapsed"
    )

    if tsv_file is not None:
        try:
            # ── Read TSV ──────────────────────────────────────────────
            df_tsv = pd.read_csv(tsv_file, sep="\t", engine="python", encoding="utf-8")

            st.success(f"✅ Loaded **{tsv_file.name}** — {df_tsv.shape[0]:,} rows × {df_tsv.shape[1]} columns")
            st.caption("Available columns: " + ", ".join(df_tsv.columns.tolist()))

            # ── Check required columns ────────────────────────────────
            required = {"Gene", "Protein Change", "Allele Freq"}
            missing  = required - set(df_tsv.columns)

            if missing:
                st.warning(f"⚠️ Missing columns: {missing}. Doing plain TSV→CSV conversion instead.")
                csv_bytes    = df_tsv.to_csv(index=False).encode("utf-8")
                csv_filename = os.path.splitext(tsv_file.name)[0] + ".csv"

            else:
                # ── Build mutation output (same logic as VSCode script) ──
                out = pd.DataFrame({
                    "gene":       df_tsv["Gene"],
                    "alteration": df_tsv["Protein Change"].astype(str).str.replace("p.", "", regex=False),
                    "vaf":        pd.to_numeric(df_tsv["Allele Freq"], errors="coerce"),
                })

                # Convert VAF from % to decimal if needed
                if out["vaf"].dropna().max() > 1:
                    out["vaf"] = (out["vaf"] / 100).round(3)

                # Drop incomplete rows
                out = out.dropna(subset=["gene", "alteration", "vaf"])
                out = out[out["alteration"] != "nan"]

                st.success(f"🧬 Processed **{len(out)}** valid mutations")

                # Preview processed table
                st.dataframe(out.head(10), use_container_width=True)

                csv_bytes    = out.to_csv(index=False).encode("utf-8")
                csv_filename = os.path.splitext(tsv_file.name)[0] + ".csv"

            st.download_button(
                label=f"⬇️ Download {csv_filename}",
                data=csv_bytes,
                file_name=csv_filename,
                mime="text/csv",
            )

        except Exception as e:
            st.error(f"❌ Could not read file: {e}")

# ── Footer ──
st.markdown("""
<div class="footer">
    Long Lung &nbsp;·&nbsp; AI-Powered Pulmonary Analysis &nbsp;·&nbsp; Built with EfficientNet &amp; U-Net
</div>
""", unsafe_allow_html=True)
