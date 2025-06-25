import os
import tempfile
import streamlit as st
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# === 🔐 Lade Umgebungsvariablen ===

form_endpoint = os.getenv("form_endpoint")
form_key = os.getenv("form_key")
openai_key = os.getenv("openai_key")
openai_endpoint = os.getenv("openai_endpoint")
openai_version = os.getenv("openai_version")
deployment_name = os.getenv("deployment_name")

# === 📋 Streamlit UI ===
st.set_page_config(page_title="Rechnungsanalyse", layout="wide")
st.title("🧾 Automatische Rechnungsauswertung (OCR + GPT)")

uploaded_file = st.file_uploader("Lade eine Rechnung hoch (PDF oder Bild)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # === OCR mit Azure Form Recognizer ===
    st.info("🔍 Führe OCR durch...")
    try:
        ocr_client = DocumentAnalysisClient(
            endpoint=form_endpoint,
            credential=AzureKeyCredential(form_key)
        )

        with open(tmp_path, "rb") as f:
            poller = ocr_client.begin_analyze_document("prebuilt-document", f)
            result = poller.result()

        invoice_text = "\n".join(
            line.content for page in result.pages for line in page.lines
        )

        # === GPT-Analyse vorbereiten ===
        st.success("✅ OCR abgeschlossen.")
        st.subheader("📄 Extrahierter Text:")
        st.text_area("OCR-Text", invoice_text, height=300)

        st.subheader("🤖 Steuerliche Bewertung")

        with st.spinner("Analysiere mit GPT..."):
            prompt = f"""
Du bist ein erfahrener deutscher Steuerberater.

Rechnungstext:
\"\"\"
{invoice_text}
\"\"\"

Bitte beantworte:
1. Ist diese Ausgabe steuerlich absetzbar für eine angestellte Person?
2. Welche Kategorie trifft zu? (z. B. Werbungskosten, Betriebsausgaben, Sonderausgaben)
3. In welches Steuerformular gehört sie?
4. In welches Feld oder Zeile wird sie typischerweise eingetragen?
5. Begründe mit §§ EStG oder offiziellen Richtlinien.
"""

            llm_client = AzureOpenAI(
                api_key=openai_key,
                api_version=openai_version,
                azure_endpoint=openai_endpoint,
            )

            response = llm_client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "system", "content": "Du bist ein deutscher Steuerberater."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            output = response.choices[0].message.content
            st.success("✅ Bewertung abgeschlossen.")
            st.text_area("KPG unverbindliche Auswertung gemäß EStG und BMF-Richtlinien", output, height=1000)

    except Exception as e:
        st.error(f"❌ Fehler bei der Analyse: {e}")
