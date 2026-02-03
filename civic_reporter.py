import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os

# --- Configuration ---
# ideally, store this in st.secrets or an environment variable
# For this script to work, you need a valid API key.
# st.secrets["GOOGLE_API_KEY"] is the recommended way to handle this in production.

st.set_page_config(page_title="Civic Issue Reporter", page_icon="🏙️")

# --- Sidebar for API Key ---
st.sidebar.header("Configuration")
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    # Fallback if running locally without secrets file
    api_key = st.text_input("Enter API Key (or set up secrets.toml)")

# Configure Gemini
if api_key:
    genai.configure(api_key=api_key)

# --- Main App Interface ---
st.title("🏙️ Civic Issue Reporter")
st.markdown("Upload a photo of a civic issue (e.g., pothole, uncollected trash), and AI will categorize it for the correct department.")

uploaded_file = st.file_uploader("Take a photo or upload an image", type=["jpg", "jpeg", "png"])

# --- Helper Function: Analyze Image ---
def analyze_image(image, key):
    try:
        genai.configure(api_key=key)
        # Use Gemini 1.5 Flash for speed and efficiency
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        Analyze this image of a civic issue. 
        Return a strict JSON object with no markdown formatting.
        The JSON must have these exact keys:
        - "Issue_Type": Short description (e.g., Pothole, Garbage, Broken Streetlight, Graffiti).
        - "Severity": "High", "Medium", or "Low".
        - "Department": The city department responsible (e.g., Public Works, Sanitation, Electrical, Parks).
        
        If the image is not relevant to civic issues, set "Issue_Type" to "Irrelevant".
        """
        
        response = model.generate_content([prompt, image])
        
        # Clean response to ensure pure JSON
        text_response = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text_response)
        
    except Exception as e:
        st.error(f"Error analyzing image: {e}")
        return None

# --- Application Logic ---
if uploaded_file is not None:
    # 1. Display the Image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
    if not api_key:
        st.warning("⚠️ Please enter your Google Gemini API Key in the sidebar to proceed.")
    else:
        with st.spinner("AI is analyzing the issue..."):
            # 2. Analyze the Image
            analysis_result = analyze_image(image, api_key)

        if analysis_result:
            # 3. Display Analysis Results
            st.divider()
            st.subheader("📋 AI Analysis Report")
            
            # Check if relevant
            if analysis_result.get("Issue_Type") == "Irrelevant":
                st.error("The AI could not identify a valid civic issue in this image.")
            else:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(label="Issue Type", value=analysis_result.get("Issue_Type", "Unknown"))
                with col2:
                    severity = analysis_result.get("Severity", "Low")
                    # Color code severity
                    color = "normal"
                    if severity == "High": color = "inverse" 
                    st.metric(label="Severity", value=severity)
                with col3:
                    st.metric(label="Assigned Dept", value=analysis_result.get("Department", "General"))

                # 4. Submit Button
                st.divider()
                if st.button("🚀 Submit Report", type="primary"):
                    dept = analysis_result.get("Department", "City Council")
                    st.success(f"✅ Report successfully sent to the **{dept}** Department!")
                    st.balloons()
                    
                    # (Optional) Log the data here to a database or CSV

                    # print(f"Logging: {analysis_result}")
