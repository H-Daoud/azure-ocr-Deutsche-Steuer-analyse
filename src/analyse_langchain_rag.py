from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

import openai

# === 1. Form Recognizer Setup ===
form_recognizer_endpoint = "https://scan-me.cognitiveservices.azure.com/"
form_recognizer_key = "FJpkrHGa9Ffkz48Ao8ljygT6MIMqI0iRVaGBD2qx5fOaa0PNly1zJQQJ99BFACYeBjFXJ3w3AAALACOGatJQ"

form_client = DocumentAnalysisClient(
    endpoint=form_recognizer_endpoint,
    credential=AzureKeyCredential(form_recognizer_key)
)

# Datei einlesen
file_path = "sample_invoice.jpg"  # oder PDF
with open(file_path, "rb") as f:
    poller = form_client.begin_analyze_document("prebuilt-document", f)
    result = poller.result()

# Rechnungstext extrahieren
invoice_text = ""
for page in result.pages:
    for line in page.lines:
        invoice_text += line.content + "\n"

print("\n--- 🧾 Rechnungstext ---")
print(invoice_text)

# === 2. Vektor-Datenbank laden ===
embedding = OpenAIEmbeddings(openai_api_key="32MZXms0KM9eQwquvvQmigYfAzeQl71NltuuslXY2M8UOlGIEFJvJQQJ99BFACYeBjFXJ3w3AAABACOGXutLQ")
vectorstore = FAISS.load_local("steuer_vektor_db", embedding)
retriever = vectorstore.as_retriever()

# === 3. Azure OpenAI Setup ===
openai.api_type = "azure"
openai.api_base = "https://openai-1001.openai.azure.com/"
openai.api_version = "2023-12-01-preview"
openai.api_key = "32MZXms0KM9eQwquvvQmigYfAzeQl71NltuuslXY2M8UOlGIEFJvJQQJ99BFACYeBjFXJ3w3AAABACOGXutLQ"
deployment_name = "2021-04-30"

llm = ChatOpenAI(deployment_name=deployment_name, temperature=0)

# === 4. Prompt mit Formularbezug ===
template = """
Du bist ein erfahrener deutscher Steuerberater.

Analysiere die folgende Rechnung:

{rechnung_text}

Beantworte:
1. Ist diese Ausgabe steuerlich absetzbar?
2. Welche Kategorie trifft zu? (z. B. Werbungskosten, Betriebsausgabe, Sonderausgabe etc.)
3. In welchem Steuerformular (z. B. Anlage N, EÜR) und in welcher Zeile wird sie eingetragen?
4. Welche Paragraphen (§ EStG) oder BMF-Schreiben gelten?

Nutze dazu auch die Informationen aus der Vektor-Datenbank (ESt-Formulare).
Antworte auf Deutsch und strukturiert.
"""

prompt = PromptTemplate(input_variables=["rechnung_text"], template=template)

# === 5. QA-Kette mit RAG ===
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt},
    return_source_documents=True
)

antwort = qa_chain(invoice_text)

# === 6. Ausgabe ===
print("\n--- 📄 Steuerliche Bewertung ---")
print(antwort["result"])

print("\n--- 📚 Quellen (aus Steuerformularen) ---")
for doc in antwort["source_documents"]:
    print(f"- Seite {doc.metadata.get('page', '?')}")
    print(doc.page_content[:300] + "...")

