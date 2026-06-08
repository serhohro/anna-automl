# 🤖 ANNA HYPERACTIVE AutoML <br> `anna-automl`

---

## 🇩🇪 GERMAN VERSION

# 🤖 ANNA HYPERACTIVE AutoML

**Version 2.0** | *Sprachgesteuerter AutoML-Assistent mit lokaler KI für Data Analysts*

---

### 📖 Über das Programm

**ANNA HYPERACTIVE AutoML** ist ein intelligenter Sprachassistent für automatisiertes maschinelles Lernen, der speziell für die schnelle Datenanalyse entwickelt wurde.

*   📊 **Daten analysieren** — Volle Unterstützung für `CSV` und `Excel`.
*   🤖 **Automatische ML-Modellauswahl** — Trainiert und vergleicht *Random Forest*, *LightGBM*, *CatBoost*, *SVM* u.a.
*   ⚡ **Hyperaktiver Modus** — Ultraschnelle Verarbeitung mit einer Latenz von `< 100 ms`.
*   🎤 **Sprachsteuerung** — Erkennt und verarbeitet mehr als 50 spezifische Sprachbefehle.
*   🧠 **Lokales LLM** — Beantwortet alle analytischen Fragen komplett lokal via *Ollama*.
*   📈 **Erweiterte Visualisierung** — Erstellt interaktive 3D-Diagramme und HTML-Dashboards.
*   🔮 **Modell-Erklärbarkeit** — Macht Vorhersagen transparent durch *SHAP* und *Feature Importance*.

---

### 🚀 Schnellstart

#### 📦 Installation

1. **Projekt klonen oder herunterladen:**
   ```bash
   git clone https://github.com/DEIN-USERNAME/anna-automl.git
   cd anna-automl

2. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt

3. **(Optional) Ollama für intelligente Antworten installieren:**
   * **Windows:** Download von [ollama.com](https://ollama.com)
   * **Mac:** `brew install ollama`
   * **Linux:** `curl -fsSL [https://ollama.com/install.sh](https://ollama.com/install.sh) | sh`

4. **Modell herunterladen und Ollama starten:**
   ```bash
   # Modell herunterladen (falls Ollama installiert ist)
   ollama pull mistral

   # Ollama starten (in einem separaten Terminal)
   ollama serve

4. **ANNA starten:**
   ```bash
   streamlit run app.py

---

## 🇬🇧 ENGLISH VERSION

# 🤖 ANNA HYPERACTIVE AutoML

**Version 2.0** | *Voice-controlled AutoML and Data Science assistant for Data Analysts with local AI*

---

### 📖 About

**ANNA HYPERACTIVE AutoML** is an intelligent voice assistant designed to automate the machine learning workflow and simplify data analysis.

*   📊 **Analyze data** — Seamless processing of `CSV` and `Excel` datasets.
*   🤖 **AutoML Engine** — Automatically trains and selects the best models (*Random Forest*, *LightGBM*, *CatBoost*, *SVM*, etc.).
*   ⚡ **Hyperactive Mode** — Lightning-fast performance with latency `< 100 ms`.
*   🎤 **Voice-Driven** — Built-in recognition for 50+ domain-specific voice commands.
*   🧠 **Local LLM Integration** — Answers data questions locally using *Ollama*.
*   📈 **Rich Visualizations** — Generates interactive 3D plots and standalone HTML dashboards.
*   🔮 **Model Explainability** — Interprets predictions using *SHAP* and *Feature Importance*.

---

### 🚀 Quick Start

#### 📦 Installation

1. **Clone or download the project:**
   ```bash
   git clone https://github.com/DEIN-USERNAME/anna-automl.git
   cd anna-automl

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt

3. **(Optional) Install Ollama for smart responses:**
   * **Windows:** download from [ollama.com](https://ollama.com)
   * **Mac:** `brew install ollama`
   * **Linux:** `curl -fsSL [https://ollama.com/install.sh](https://ollama.com/install.sh) | sh`

4. **Download the model and run Ollama:**
   ```bash
   # Download the model (if Ollama is installed)
   ollama pull mistral

   # Run Ollama (in a separate terminal)
   ollama serve

5. **Launch ANNA:**
   ```bash
   streamlit run app.py
