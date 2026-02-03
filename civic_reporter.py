import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Civic Issue Reporter",
    page_icon="🏙️",
    layout="centered"
)

# ------------------ SIDEBAR ------------------
st.sidebar.title("⚙️ Configuration")

use_mock_ai = st.sidebar.checkbox(
    "Use Demo AI (Safe Mode)",
    value=True,
    help="Turn OFF only if you are confident your API key will work"
)

api_key = ""
if not use_mock_ai:
    api_key = st.sidebar.text_input(
        "Google Gemini API Key",
        type="password"
    )

# ------------------ TITLE ------------------
st.title("🏙️ Civic Issue Reporter")
st.write(
    "Upload a photo of a civic issue (pothole, garbage, broken streetlight). "
    "AI will automatically classify and prioritize it."
)

# ------------------ FILE UPLOAD ------------------
uploaded_file = st.file_uploader(
    "📸 Upload an image",
    type=["jpg", "jpeg", "png"]
)

# ------------------ MOCK AI (SAFE FALLBACK) ------------------
def mock_ai_response():
    return {
        "Issue_Type": "Pothole",
        "Severity": "High",
        "Department": "Public Works"
    }

# ------------------ REAL AI FUNCTION ------------------
def analyze_image_with_gemini(image, key):
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = """
        You are a civic inspector AI.

        Analyze the image and return ONLY valid JSON with:
        {
          "Issue_Type": "Pothole / Garbage / Broken Streetlight / Graffiti / Irrelevant",
          "Severity": "High / Medium / Low",
          "Department": "Public Works / Sanitation / Electrical / Parks"
        }
        """

        response = model.generate_content([prompt, image])

        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "")

        return json.loads(text)

    except Exception as e:
        st.warning("⚠️ AI failed, switching to demo response.")
        return mock_ai_response()

# ------------------ MAIN LOGIC ------------------
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("🔍 Analyze Issue"):
        with st.spinner("Analyzing issue..."):
            if use_mock_ai:
                result = mock_ai_response()
            else:
                if not api_key:
                    st.error("Please enter an API key or enable Demo AI.")
                    st.stop()
                result = analyze_image_with_gemini(image, api_key)

        # ------------------ RESULTS ------------------
        st.divider()
        st.subheader("📋 AI Analysis Report")

        if result["Issue_Type"] == "Irrelevant":
            st.error("No valid civic issue detected.")
        else:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Issue Type", result["Issue_Type"])
            with col2:
                st.metric("Severity", result["Severity"])
            with col3:
                st.metric("Department", result["Department"])

            st.divider()

            if st.button("🚀 Submit Report", type="primary"):
                st.success(
                    f"Report sent to **{result['Department']} Department**"
                )
                st.balloons()

# ------------------ ADMIN DASHBOARD (DEMO) ------------------
st.divider()
st.header("🛠️ Admin Dashboard (Demo)")

st.table({
    "Issue": ["Pothole", "Garbage"],
    "Severity": ["High", "Medium"],
    "Status": ["Open", "In Progress"],
    "Department": ["Public Works", "Sanitation"]
})
