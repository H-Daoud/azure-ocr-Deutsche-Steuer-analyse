# azure-ocr-Deutsche-Steuer-analyse
OCR-basiertes Tool zur steuerlichen Analyse deutscher Rechnungen mit Azure Form Recognizer und GPT“

# 1. open VS and Drop & Drag Github Folder

# 1. setup your virtual environment
# macOS/Linux:
python3 -m venv venv
source venv/bin/activate
# Windows (CMD):
cmd
venv\Scripts\activate.bat
# Windows (PowerShell):
venv\Scripts\Activate.ps1

# 3. Install required packages
pip install --upgrade pip

pip install -r requirments.txt

# 4. Systemtools via Homebrew
brew install tesseract
brew install poppler

# 5. Python-Umgebung vorbereiten
python3 -m venv venv
source venv/bin/activate

# 6. Python-Pakete installieren
pip install -r requirements.txt

# 7. (optional) Python-Pakete installieren direct sh script
setup.sh (macOS-kompatibel) some packages can not installed by requirments.txt , there for run ./setp.sh to install the rest of required packages.  

| Komponente                | Technologie/Lib                       | Aufgabe                                     |
| ------------------------- | ------------------------------------- | ------------------------------------------- |
| Dokumenten-Vektorisierung | `LangChain`, `LlamaIndex`, `Haystack` | Wandle Gesetzestexte/Rechnungen in Vektoren |
| Vektor-Datenbank          | `FAISS`, `ChromaDB`, `Weaviate`       | Ähnlichkeitssuche                           |
| LLM-Modell (local/cloud)  | `OpenAI GPT`, `Mistral`, `LLama.cpp`  | Antwort generieren                          |
| UI oder API               | `Streamlit`, `FastAPI`, `Gradio`      | Nutzerinterface / Abfrage                   |
| Dokumentenquelle          | `PDF`, `HTML`, `txt`, OCR             | EStG, BMF-Schreiben, Urteile, Rechnungen    |
=======
# azure-ocr-Deutsche-Steuer-analyse
OCR-basiertes Tool zur steuerlichen Analyse deutscher Rechnungen mit Azure Form Recognizer und GPT“
>>>>>>> b587bdaafbdf8d056220456081b379b5ac8427cb
