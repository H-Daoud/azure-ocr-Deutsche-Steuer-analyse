import os
import logging
from openai import AzureOpenAI
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# === 🔧 Setup Logging: Konsole + Datei ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),                        # Konsole
        logging.FileHandler("app.log", mode="w")        # Log-Datei
    ]
)

# === 🔐 Lade Umgebungsvariablen ===
load_dotenv()
form_endpoint = os.getenv("form_endpoint")
form_key = os.getenv("form_key")
openai_key = os.getenv("openai_key")
openai_endpoint = os.getenv("openai_endpoint")
openai_version = os.getenv("openai_version")
deployment_name = os.getenv("deployment_name")

# === 📂 Eingabedatei prüfen ===
from pathlib import Path
import logging

# Setup logging (optional but useful)
logging.basicConfig(level=logging.INFO)

# Define the file path using pathlib
file_path = Path("sample_invoice.jpg")

# Check if file exists
if not file_path.exists():
    logging.error(f"❌ Datei nicht gefunden: {file_path}")
    raise FileNotFoundError(f"❌ Datei nicht gefunden: {file_path}")

# Optional: Log success
logging.info(f"📄 Eingabedatei gefunden: {file_path}")

# === 📥 Azure Form Recognizer Client initialisieren ===
# === 🧾 OCR mit Azure Form Recognizer ===
logging.info("📥 Starte OCR-Analyse mit Azure Form Recognizer...")
ocr_client = DocumentAnalysisClient(
    endpoint=form_endpoint,
    credential=AzureKeyCredential(form_key)
)

with open(file_path, "rb") as f:
    poller = ocr_client.begin_analyze_document("prebuilt-document", f)
    result = poller.result()

invoice_text = "\n".join(
    line.content for page in result.pages for line in page.lines
)

logging.info("--- 🧾 Extrahierter Rechnungstext ---")
logging.info(invoice_text)

# === 🤖 Steuerliche Analyse via Azure OpenAI ===
prompt = f"""
Du bist ein erfahrener deutscher Steuerberater. Analysiere den folgenden Rechnungstext und beantworte präzise die folgenden steuerlichen Fragen.

Rechnungstext:
\"\"\"
{invoice_text}
\"\"\"

Bitte beantworte:
1. Ist diese Ausgabe steuerlich absetzbar für eine angestellte Person?
2. Welche Kategorie trifft zu? (z. B. Werbungskosten, Betriebsausgaben, Sonderausgaben, etc.)
3. In welches Steuerformular gehört sie? (z. B. Anlage N, EÜR, S)
4. In welches Feld oder Zeile wird sie typischerweise eingetragen?
5. Begründe mit §§ EStG oder offiziellen Richtlinien (z. B. BMF-Schreiben).
"""

logging.info("🤖 Sende Anfrage an Azure OpenAI...")

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

logging.info("--- 📄 Steuerliche Bewertung ---")
logging.info(response.choices[0].message.content)
# === ✅ Abschluss ===