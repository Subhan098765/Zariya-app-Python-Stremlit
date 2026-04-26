# Zariya B2B Marketplace — Cloud Run Deployment Guide

## Project Structure

```
zariya_streamlit/
├── app.py              # Main entry point & router
├── auth.py             # Google OAuth + KYC registration
├── wholesaler.py       # Wholesaler dashboard
├── shopkeeper.py       # Shopkeeper dashboard + AI Guru
├── payments.py         # Mock payment gateway
├── data_store.py       # JSON persistence (GCS-ready)
├── data/
│   ├── users.json      # User profiles (KYC)
│   └── inventory.json  # Product listings (pre-seeded)
├── .streamlit/
│   └── config.toml     # Streamlit server config
├── requirements.txt
└── Dockerfile
```

---

## Environment Variables

Set these before running locally or in Cloud Run:

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Your Gemini 1.5 Flash API key |
| `CLIENT_ID` | Google OAuth Client ID |

---

## Run Locally

```bash
cd zariya_streamlit

# Install dependencies
pip install -r requirements.txt

# Set env vars (Windows PowerShell)
$env:GEMINI_API_KEY = "your_key_here"
$env:CLIENT_ID = "your_client_id_here"

# Run
streamlit run app.py
```

Then open http://localhost:8501

---

## Docker Build & Run Locally

```bash
cd zariya_streamlit

docker build -t zariya-b2b .

docker run -p 8080:8080 \
  -e GEMINI_API_KEY="your_key" \
  -e CLIENT_ID="your_client_id" \
  zariya-b2b
```

Then open http://localhost:8080

---

## Deploy to Google Cloud Run

### 1. Enable APIs
```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
```

### 2. Build & Push Image
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/zariya-b2b
```

### 3. Deploy
```bash
gcloud run deploy zariya-b2b \
  --image gcr.io/YOUR_PROJECT_ID/zariya-b2b \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars GEMINI_API_KEY=your_key,CLIENT_ID=your_client_id \
  --memory 512Mi \
  --cpu 1
```

### 4. Set Google OAuth Redirect URI

In Google Cloud Console → APIs & Services → Credentials:
- Add your Cloud Run URL to **Authorized redirect URIs**:  
  `https://your-service-url.run.app/oauth2callback`

---

## Upgrading to Google Cloud Storage

In `data_store.py`, the `upload_to_gcs()` and `download_from_gcs()` stubs are ready.

1. Uncomment `google-cloud-storage` in `requirements.txt`
2. Implement the stubs (code provided in comments)
3. Replace `_read_json` / `_write_json` calls to use GCS

---

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. APIs & Services → Credentials → Create OAuth 2.0 Client ID
3. Application type: **Web application**
4. Set your `CLIENT_ID` environment variable
5. Streamlit uses `st.login('google')` — ensure your redirect URIs are configured
