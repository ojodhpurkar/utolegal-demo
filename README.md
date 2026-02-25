# AutoLegal Prototype (Promptathon 2026)

This is a working prototype for the "Contract Obligation Extraction" use case, designed to demonstrate what a winning Promptathon submission should look like. It uses Google Gemini 1.5 Flash to automatically extract obligations, SLAs, penalties, and renewal dates from a vendor contract.

## Prerequisites
1. Python 3.9+
2. A free Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

## How to Run Locally

1. **Install dependencies:**
   Open your terminal in this directory (`autolegal_demo`) and run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Streamlit App:**
   Run the following command:
   ```bash
   streamlit run app.py
   ```

3. **Use the App:**
   - The app will open in your browser automatically (usually at `http://localhost:8501`).
   - Paste your Gemini API Key into the sidebar.
   - Upload any sample contract PDF.
   - Click "Extract Obligations" and wait 10-20 seconds.
   - View the results and download them as a CSV.
