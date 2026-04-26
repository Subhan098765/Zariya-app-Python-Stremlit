# Zariya B2B Marketplace 🌿
### آپ کا کاروباری ساتھی

Zariya is a professional B2B marketplace built with **Python** and **Streamlit**, optimized for deployment on **Google Cloud Run**. It connects Wholesalers with Shopkeepers through a secure, AI-powered platform tailored for the Pakistani FMCG ecosystem.

## 🚀 Key Features
- **Authentication**: Mandatory Google Login (Demo Mode available for local testing).
- **KYC Registration**: Mandatory profile completion with CNIC and business location validation.
- **Dual Dashboards**: 
  - **Wholesalers**: Add products, manage inventory (Unilever, Nestlé, etc.).
  - **Shopkeepers**: Searchable marketplace, searchable product gallery, and AI Guru.
- **AI Guru**: Gemini 2.0 Flash integration for smart stock suggestions and price analysis in English and Urdu.
- **Payments**: Mock integration with **Raast**, **JazzCash**, and **NayaPay Arc**.
- **Cloud Native**: Ready for Google Cloud Run with Docker support and GCS-ready persistence.

## 🛠️ Setup & Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Set your `GEMINI_API_KEY` for the AI Guru.
   ```bash
   export GEMINI_API_KEY="your_api_key"
   ```

3. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## 📦 Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to Google Cloud Run.

## 📄 Data Management
Uses local `users.json` and `inventory.json` for rapid demoing, with abstracted logic for easy migration to Google Cloud Storage.
