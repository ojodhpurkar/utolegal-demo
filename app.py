import streamlit as st
import google.generativeai as genai
import PyPDF2
import json
import pandas as pd

st.set_page_config(page_title="AutoLegal: Contract Extractor", layout="wide")

st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
st.sidebar.markdown("""
**Note:** You can get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/).
""")

selected_model_name = None
if api_key:
    genai.configure(api_key=api_key)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if available_models:
            # Try to default to a flash model if available
            default_idx = 0
            for i, m in enumerate(available_models):
                if '1.5-flash' in m:
                    default_idx = i
                    break
            selected_model = st.sidebar.selectbox("Select Gemini Model", available_models, index=default_idx)
            
            if selected_model and selected_model.startswith('models/'):
                selected_model_name = selected_model[7:]
            else:
                selected_model_name = selected_model
        else:
            st.sidebar.error("No compatible models found for this API key.")
    except Exception as e:
        st.sidebar.error(f"Error fetching models. Please check your API key.")

st.title("AutoLegal: Contract Obligation Extraction")
st.markdown("Upload a Vendor Contract (PDF) to automatically extract key obligations, SLAs, penalties, and renewal terms into a structured format.")

uploaded_file = st.file_uploader("Upload Contract PDF", type=["pdf"])

if st.button("Extract Obligations"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar to proceed.")
    elif not selected_model_name:
        st.error("Please select a valid Gemini Model from the sidebar.")
    elif not uploaded_file:
        st.error("Please upload a PDF contract.")
    else:
        try:
            model = genai.GenerativeModel(selected_model_name)
            
            # Read PDF content
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            contract_text = ""
            for i, page in enumerate(pdf_reader.pages[:30]):
                contract_text += f"\n--- Page {i+1} ---\n"
                contract_text += page.extract_text() + "\n"
                
            prompt = """
            You are an expert legal AI assistant. Your task is to extract key obligations, SLAs, penalties, and renewal/termination clauses from the following contract text.
            
            Return the output STRICTLY as a JSON array of objects. Do not include any other text before or after the JSON.
            Each object should have the following exact keys:
            - "Clause Type" (string, e.g., 'Obligation', 'SLA Penalty', 'Termination', 'Renewal')
            - "Description" (string, a concise summary of the extracted clause)
            - "Page Reference" (string, the page number where you found this based on the '--- Page X ---' markers)

            Contract Text:
            """ + contract_text
            
            with st.spinner(f"Analyzing contract using {selected_model_name}..."):
                response = model.generate_content(prompt)
                
            out_text = response.text.strip()
            if out_text.startswith("```json"):
                out_text = out_text[7:]
            elif out_text.startswith("```"):
                out_text = out_text[3:]
            if out_text.endswith("```"):
                out_text = out_text[:-3]
                
            data = json.loads(out_text.strip())
            
            st.success("Extraction Complete!")
            st.table(data)
            
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name='extracted_obligations.csv',
                mime='text/csv',
            )
            
        except json.JSONDecodeError:
            st.error("The AI did not return a valid JSON format. It returned:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Error processing document: {e}")
