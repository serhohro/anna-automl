## 🇩🇪 GERMAN VERSION

```markdown
# 🤖 ANNA HYPERACTIVE AutoML

**Version 2.0** | Sprachgesteuerter AutoML-Assistent mit lokaler KI

## 📖 Über das Programm

ANNA HYPERACTIVE AutoML ist ein intelligenter Sprachassistent für automatisiertes maschinelles Lernen. Das Programm kann:

- 📊 **Daten analysieren** (CSV, Excel)
- 🤖 **Automatisch die besten ML-Modelle auswählen** (Random Forest, LightGBM, CatBoost, SVM u.a.)
- ⚡ **Im hyperaktiven Modus arbeiten** mit einer Latenz < 100 ms
- 🎤 **Sprachbefehle verstehen** (mehr als 50 Befehle)
- 🧠 **Alle Fragen beantworten** über lokales LLM (Ollama)
- 📈 **3D-Diagramme und HTML-Dashboards erstellen**
- 🔮 **Vorhersagen erklären** (SHAP, Feature Importance)

## 🚀 Schnellstart

### Installation

```bash
# 1. Projekt klonen oder herunterladen

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. (Optional) Ollama für intelligente Antworten installieren
# Windows: Download von https://ollama.com
# Mac: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# 4. Modell herunterladen (falls Ollama installiert ist)
ollama pull mistral

# 5. Ollama starten (in einem separaten Terminal)
ollama serve

# 6. ANNA starten
streamlit run app.py

---

## 🇬🇧 ENGLISH VERSION

# 🤖 ANNA HYPERACTIVE AutoML

**Version 2.0** | Voice-controlled AutoML assistant with local AI

## 📖 About

ANNA HYPERACTIVE AutoML is an intelligent voice assistant for automated machine learning. The program can:

- 📊 **Analyze data** (CSV, Excel)
- 🤖 **Automatically select the best ML models** (Random Forest, LightGBM, CatBoost, SVM, and more)
- ⚡ **Run in hyperactive mode** with latency < 100 ms
- 🎤 **Understand voice commands** (50+ commands)
- 🧠 **Answer any questions** via local LLM (Ollama)
- 📈 **Create 3D plots and HTML dashboards**
- 🔮 **Explain predictions** (SHAP, Feature Importance)

## 🚀 Quick Start

### Installation

```bash
# 1. Clone or download the project

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Install Ollama for smart responses
# Windows: download from https://ollama.com
# Mac: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# 4. Download the model (if Ollama is installed)
ollama pull mistral

# 5. Run Ollama (in a separate terminal)
ollama serve

# 6. Launch ANNA
streamlit run app.py
