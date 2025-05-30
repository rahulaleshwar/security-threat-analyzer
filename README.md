# 🔐 Security Threat Analyzer

A smart DevSecOps helper powered by Google Vertex AI Gemini. This app analyzes security-related files like Dockerfiles, logs, and vulnerability scan reports. It detects misconfigurations, highlights potential risks, and generates PDF reports — all in a few clicks.

---

## 🛠️ Technologies Used

- [Streamlit](https://streamlit.io/) – UI for user interaction  
- [Vertex AI Gemini](https://cloud.google.com/vertex-ai/docs/generative-ai/overview) – Security analysis via generative AI  
- [Google Cloud Firestore](https://firebase.google.com/docs/firestore) – Storing historical reports  
- [xhtml2pdf](https://github.com/xhtml2pdf/xhtml2pdf) – Markdown to PDF conversion  
- [Google Cloud Run](https://cloud.google.com/run) – Deployment platform  
- [Artifact Registry](https://cloud.google.com/artifact-registry) – Secure Docker image hosting  

---

## ✨ Features

- 📤 Upload Dockerfiles, logs, or vulnerability scan reports  
- 🤖 AI-generated security analysis using Gemini  
- 🛡️ Threat scoring: Low, Medium, High, Critical  
- 📄 Download detailed PDF reports  
- ☁️ Save reports to Firestore  
- 🌐 One-click deployable to Google Cloud  

---

## ⚙️ How It Works

1. User uploads a file (e.g., Dockerfile or log).
2. The app sends the content to Gemini (Vertex AI) for analysis.
3. Gemini generates a detailed security report with remediation steps.
4. The app assigns a threat score and saves the result to Firestore.
5. User can download a clean PDF report of the analysis.

---

## 📦 Prerequisites

Before running or deploying the app:

- Python 3.9+
- Google Cloud Project with:
  - Vertex AI API enabled
  - Firestore (Native Mode)
  - Artifact Registry
  - Cloud Run
- `gcloud` CLI installed and authenticated
- Billing enabled on your project

---

## 🚀 Deploy to Google Cloud

### 1. Enable Required APIs
```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com firestore.googleapis.com aiplatform.googleapis.com
```
### 2. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create streamlit-apps \
  --repository-format=docker \
  --location=us \
  --description="Docker repo for Streamlit apps"
```

### 3. Create Firestore Database
```bash
gcloud firestore databases create \
  --project=YOUR_PROJECT_ID \
  --region=us-central1 \
  --database=default
```

### 4. Build & Push Docker Image
```bash
gcloud auth configure-docker us-docker.pkg.dev

docker build -t us-docker.pkg.dev/YOUR_PROJECT_ID/streamlit-apps/security-threat-analyzer .

docker push us-docker.pkg.dev/YOUR_PROJECT_ID/streamlit-apps/security-threat-analyzer
```
### 5. Deploy to Cloud Run
```bash
gcloud run deploy security-threat-analyzer \
  --image us-docker.pkg.dev/YOUR_PROJECT_ID/streamlit-apps/security-threat-analyzer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501
```
---

## 🧪 Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/rahulaleshwar/security-threat-analyzer.git
cd security-threat-analyzer
```
### 2. Install Requirements
```bash
pip install -r requirements.txt
```
### 3. Set Google Project Environment
```bash
export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
```
### 4. Run the App
```bash
streamlit run app.py
```
---

## 🙌 Acknowledgments

- Vertex AI for the generative analysis engine
- Streamlit for fast and beautiful UIs
- Firestore for secure cloud data storage
- xhtml2pdf for clean report generation

---

## 📬 Contact

For questions, suggestions, or feedback, feel free to open an issue or contact.
