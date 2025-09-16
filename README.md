# CodeSentinel AI

**A multi-layered, AI-powered guardian for your software supply chain.**

CodeSentinel AI is a comprehensive security tool designed to detect and remediate threats in Python package dependencies. It moves beyond traditional scanners by using a multi-layered approach that analyzes package metadata, author reputation, source code, and a predictive AI model to generate a holistic trust score.

---

## Key Features

* **Four-Layer Analysis Engine:** Combines PyPI metadata, GitHub author reputation, dependency scanning, and static code analysis for deep, contextual security insights.
* **Predictive AI Model:** Utilizes a custom-trained Machine Learning model to predict the risk of new and unknown packages based on learned patterns.
* **Autonomous Remediation Agent:** Doesn't just find problems—it fixes them. The agent automatically creates a branch, applies a fix, and opens a Pull Request when it discovers a vulnerable package.
* **Interactive Web Dashboards:** Two separate, modern dashboards for viewing the multi-layer scan results and for running on-demand predictions with the AI model.
* **Automated CI/CD Integration:** A fully functional GitHub Action that automatically scans every code push, acting as a security gate to prevent risky code from being merged.

---

##  Project Architecture

CodeSentinel AI was built with an evolutionary, multi-layered architecture.

### 1. The Rule-Based Analysis Engine
This is the core scanner that performs a deep investigation using four distinct layers of defense.
* **Layer 1: PyPI Metadata Analysis:** A baseline check for professionalism and legitimacy (author, homepage, version history).
* **Layer 2: GitHub Reputation Analysis:** A deep dive into the author's credibility by analyzing their GitHub profile (followers, account age).
* **Layer 3: Dependency Scanning:** An analysis of a package's "associates"—the other libraries it depends on—to flag suspicious requirements.
* **Layer 4: Static Code Analysis:** A full forensic scan of the package's source code to find dangerous commands (`os.system`, `eval`, etc.) hidden in the files.

### 2. The AI Predictor
To move beyond static rules, we built a true predictive engine.
* **Custom Dataset:** We created a dataset of both known-safe packages and hypothetical malicious packages.
* **Model Training:** We trained a `RandomForestClassifier` model using `scikit-learn` to recognize the patterns of a risky package.
* **Live Predictions:** The final model is used in our AI dashboard to provide on-demand risk predictions with a confidence score.

### 3. The Auto-Remediation Agent
This is the final, agentic layer that allows CodeSentinel to act autonomously.
* **Trigger:** The agent is triggered by our GitHub Action when a low-scoring package is found.
* **Observe-Think-Act:** It identifies the vulnerable package, finds a newer version, and formulates a plan.
* **Execution:** Using the GitHub API, it autonomously creates a new branch, updates the `requirements.txt` file, and opens a detailed Pull Request to fix the vulnerability.

---

##  Dashboards & CI/CD

### Rule-Based Analysis Dashboard
This dashboard provides a detailed breakdown of the 4-layer scan for a project's `requirements.txt`.
*(Your Screenshot of the first dashboard `app.py` here)*

### AI Predictor Dashboard
This dashboard allows for on-demand analysis of any single PyPI package using the trained ML model.
*(Your Screenshot of the second dashboard `ai_dashboard.py` here)*

### Automated CI/CD Integration
Our GitHub Action provides a fully automated security gate, failing the build if a vulnerability is detected.
*(Your Screenshot of a failed/successful GitHub Action run here)*

---

## 🛠 How to Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/shahirun-x/CodeSentinel-AI.git](https://github.com/shahirun-x/CodeSentinel-AI.git)
    cd CodeSentinel-AI
    ```
2.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r tool_requirements.txt
    ```
4.  **Set Environment Variable:** For the agent to work, you need a GitHub Personal Access Token (PAT).
    ```powershell
    $env:GITHUB_PAT="your_token_here" # Windows PowerShell
    ```
5.  **Run the Dashboards:**
    ```bash
    # To run the rule-based dashboard
    python app.py

    # To run the AI predictor dashboard
    python ai_dashboard.py --port 5001
    ```

---

##  Technology Stack
* **Backend:** Python, Flask
* **Machine Learning:** Scikit-learn, Pandas, Joblib
* **Frontend:** HTML, Bootstrap 5
* **APIs:** PyPI API, GitHub API
* **CI/CD:** GitHub Actions
