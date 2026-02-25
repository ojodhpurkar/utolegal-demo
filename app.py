import streamlit as st
import google.generativeai as genai
import json
import time

# --- Page Config ---
st.set_page_config(
    page_title="ContractIQ — Promptathon 2026 Demo",
    page_icon="📄",
    layout="wide"
)

# --- Styling ---
st.markdown("""
<style>
    .main { background-color: #f8f9fb; }
    .stTextArea textarea { font-size: 14px; }
    .result-card {
        background: white;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-left: 4px solid #4F46E5;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .risk-high { border-left-color: #EF4444; }
    .risk-medium { border-left-color: #F59E0B; }
    .risk-low { border-left-color: #10B981; }
    .metric-box {
        background: white;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-high { background: #FEE2E2; color: #DC2626; }
    .badge-medium { background: #FEF3C7; color: #D97706; }
    .badge-low { background: #D1FAE5; color: #059669; }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("## 📄 ContractIQ")
st.markdown("**Promptathon 2026 POC** — AI-powered contract obligation extractor for GCC legal & compliance teams")
st.divider()

# --- Sidebar: API Key ---
with st.sidebar:
    st.markdown("### ⚙️ Setup")
    api_key = st.text_input("Gemini API Key", type="password", placeholder="Paste your free Gemini API key")
    st.caption("Get a free key at [aistudio.google.com](https://aistudio.google.com)")
    st.divider()
    st.markdown("### 📊 Business Value Estimator")
    contracts_per_year = st.slider("Contracts reviewed per year", 50, 2000, 500, 50)
    hours_per_contract = st.slider("Current hours per contract", 1, 8, 3)
    hourly_cost = st.slider("Avg. cost per hour (₹)", 500, 3000, 1200, 100)
    time_saved_pct = 0.70
    hours_saved = contracts_per_year * hours_per_contract * time_saved_pct
    cost_saved = hours_saved * hourly_cost
    st.metric("Hours saved / year", f"{int(hours_saved):,}")
    st.metric("Cost saved / year", f"₹{int(cost_saved):,}")
    st.caption("Assumes 70% time reduction based on benchmark studies")

# --- Sample Contract ---
SAMPLE_CONTRACT = """SERVICE AGREEMENT

This Agreement is entered into on 1st January 2025 between TechCorp India Pvt Ltd ("Service Provider") and GlobalRetail GCC ("Client").

1. PAYMENT TERMS
The Client shall pay all invoices within 30 days of receipt. Late payments will attract a penalty of 2% per month. The Client must notify the Service Provider of any disputes within 7 days of receiving the invoice.

2. CONFIDENTIALITY
Both parties agree to maintain strict confidentiality of all proprietary information for a period of 3 years after termination of this agreement. The Service Provider shall not disclose any client data to third parties without written consent.

3. INTELLECTUAL PROPERTY
All work products, code, and deliverables created under this agreement shall remain the exclusive property of the Client upon full payment. The Service Provider retains no rights to reuse or repurpose these materials.

4. TERMINATION
Either party may terminate this agreement with 60 days written notice. In case of breach, the non-breaching party may terminate immediately and claim damages up to 6 months of contract value.

5. LIABILITY
The Service Provider's total liability under this agreement shall not exceed the total fees paid in the preceding 3 months. Neither party shall be liable for indirect or consequential damages.

6. GOVERNING LAW
This agreement shall be governed by the laws of Maharashtra, India. All disputes shall be resolved through arbitration in Mumbai.
"""

# --- Main Layout ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📝 Input Contract")
    use_sample = st.toggle("Use sample contract", value=True)
    
    if use_sample:
        contract_text = st.text_area("Contract Text", value=SAMPLE_CONTRACT, height=400)
    else:
        contract_text = st.text_area("Paste your contract here", height=400, placeholder="Paste contract text...")
    
    analyze_btn = st.button("🔍 Analyze Contract", type="primary", use_container_width=True)

with col2:
    st.markdown("### 📋 Extracted Obligations")
    
    if analyze_btn:
        if not api_key:
            st.error("Please enter your Gemini API key in the sidebar.")
        elif not contract_text.strip():
            st.error("Please paste a contract to analyze.")
        else:
            with st.spinner("Analyzing contract..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.0-flash")
                    
                    # The core prompt — this is what students engineer
                    prompt = f"""You are a legal AI assistant for a GCC compliance team. 
Analyze the following contract and extract all obligations, risks, and key dates.

Return ONLY a valid JSON object with this exact structure:
{{
  "summary": "2 sentence plain English summary of the contract",
  "obligations": [
    {{
      "clause": "clause name",
      "obligation": "what must be done",
      "party_responsible": "Client or Service Provider",
      "deadline": "specific deadline if mentioned, else null",
      "risk_level": "High or Medium or Low",
      "risk_reason": "why this risk level"
    }}
  ],
  "key_dates": ["list of important dates or deadlines"],
  "overall_risk": "High or Medium or Low",
  "recommended_actions": ["list of 3 actions the compliance team should take"]
}}

CONTRACT:
{contract_text}"""

                    response = model.generate_content(prompt)
                    raw = response.text.strip()
                    
                    # Clean JSON if wrapped in markdown
                    if raw.startswith("```"):
                        raw = raw.split("```")[1]
                        if raw.startswith("json"):
                            raw = raw[4:]
                    
                    data = json.loads(raw)
                    
                    # Summary
                    st.markdown(f"""
                    <div class="result-card">
                        <strong>📌 Summary</strong><br><br>
                        {data.get('summary', '')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Overall risk
                    risk = data.get('overall_risk', 'Medium')
                    risk_color = {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}.get(risk, "badge-medium")
                    st.markdown(f"**Overall Risk:** <span class='badge {risk_color}'>{risk}</span>", unsafe_allow_html=True)
                    st.markdown("")
                    
                    # Obligations table
                    st.markdown("**Extracted Obligations**")
                    obligations = data.get("obligations", [])
                    for ob in obligations:
                        r = ob.get("risk_level", "Medium")
                        card_class = {"High": "risk-high", "Medium": "risk-medium", "Low": "risk-low"}.get(r, "")
                        badge_class = {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}.get(r, "")
                        deadline_text = f"⏰ {ob.get('deadline')}" if ob.get('deadline') else ""
                        st.markdown(f"""
                        <div class="result-card {card_class}">
                            <strong>{ob.get('clause', '')}</strong> &nbsp;
                            <span class='badge {badge_class}'>{r} Risk</span><br>
                            <small style='color:#666'>{ob.get('party_responsible','')}</small><br><br>
                            {ob.get('obligation', '')}<br>
                            <small style='color:#888'><em>{ob.get('risk_reason','')}</em></small>
                            {"<br><small>" + deadline_text + "</small>" if deadline_text else ""}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Recommended actions
                    st.markdown("**✅ Recommended Actions**")
                    for action in data.get("recommended_actions", []):
                        st.markdown(f"- {action}")
                    
                    # Key dates
                    if data.get("key_dates"):
                        st.markdown("**📅 Key Dates & Deadlines**")
                        for d in data.get("key_dates", []):
                            st.markdown(f"- {d}")

                except json.JSONDecodeError:
                    st.error("Could not parse the AI response. Try again.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.info("Configure your API key in the sidebar, then click **Analyze Contract** to see results.")
        st.markdown("""
        **What this demo shows:**
        - Upload any contract text
        - AI extracts all obligations, parties, deadlines
        - Risk-scores each clause automatically  
        - Outputs a structured table ready for case management
        - Estimates hours and cost saved per year
        
        *Built with: Streamlit + Gemini API (free tier)*
        """)

# --- Footer ---
st.divider()
st.caption("Promptathon 2026 · Infocepts × NASSCOM × Ramdeobaba University · Built with Streamlit + Gemini API (Free Tier)")
