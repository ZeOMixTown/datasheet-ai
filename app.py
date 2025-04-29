import streamlit as st
import openai
from docx import Document
from docx.shared import Pt
from io import BytesIO
from fpdf import FPDF

# --- Streamlit page settings ---
st.set_page_config(page_title="Datasheet Generator", layout="centered")
st.title("📄 AI-Based Datasheet Generator")

# --- User input form ---
st.header("1. Product Input")

# Logo upload
company_logo = st.file_uploader("Upload company logo (PNG or JPG)", type=["png", "jpg", "jpeg"])

product_name = st.text_input("Product Name")
sensor_type = st.selectbox("Sensor Type", ["Temperature", "Pressure", "Gas", "Accelerometer", "Other"])
dimensions = st.text_input("Dimensions (e.g., 50×30×10 mm)")
weight = st.text_input("Weight (g)")
power = st.text_input("Power Supply (e.g., 3.3 V / 150 mA)")
measurement_range = st.text_input("Measurement Range (e.g., -40°C to 125°C)")
sensitivity = st.text_input("Sensitivity (e.g., 10 mV/°C)")
accuracy = st.text_input("Accuracy (e.g., ±1°C)")
response_time = st.text_input("Response Time (e.g., <1s)")
signal_type = st.text_input("Output Signal (e.g., Analog / I2C / SPI)")

features = st.text_area("Key Features (comma separated)")
applications = st.text_area("Target Applications (comma separated)")


# --- Datasheet generation with GPT ---
if st.button("🔧 Generate Datasheet"):
    with st.spinner("Generating content with GPT..."):

        # Prompt template with proper structure and formatting instructions
        prompt = f"""
You are a professional technical writer specializing in sensor datasheets for electronic devices.
Generate a precise and technically accurate datasheet in clean markdown format.
The datasheet must comply with industrial documentation standards (IEC, JEDEC, IPC) and be structured as follows:

---

### 1. Product Overview
Provide a short, factual description (1–2 sentences) of the sensor’s purpose and main capabilities.

### 2. Key Features
Provide 5–10 concise bullet points with product highlights. Avoid duplication from other sections.

### 3. Mechanical Specifications
Present the following:
- Dimensions: {dimensions}
- Weight: {weight}
- Mounting Type (if applicable)

### 4. Electrical Characteristics
Include:
- Power Supply: {power}
- Output Signal Type: {signal_type}

### 5. Sensing Performance
Detail the following:
- Measurement Range: {measurement_range}
- Sensitivity: {sensitivity}
- Accuracy: {accuracy}
- Response Time: {response_time}

### 6. Environmental Ratings
Include any applicable items:
- Operating Temperature
- IP Rating
- Humidity Range

### 7. Regulatory & Compliance
List any certifications, such as:
- CE, RoHS, FCC, UL
- ESD protection

### 8. Applications
List relevant usage domains:
{applications}

---

**Formatting instructions:**
- Use markdown headings and bullet points where appropriate.
- Keep tone strictly technical and formal (no marketing language).
- Use SI units.
- If a field is empty, omit that line entirely.
- Never invent data — use only provided input.

---
Provided information:
- Product Name: {product_name}
- Sensor Type: {sensor_type}
- Dimensions: {dimensions}
- Weight: {weight}
- Power: {power}
- Measurement Range: {measurement_range}
- Sensitivity: {sensitivity}
- Accuracy: {accuracy}
- Response Time: {response_time}
- Output Signal Type: {signal_type}
- Features: {features}
- Applications: {applications}
"""

        # Call OpenAI with updated API (version >= 1.0.0)
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if available
            messages=[
                {"role": "system", "content": "You are a technical writer."},
                {"role": "user", "content": prompt}
            ]
        )

        datasheet = response.choices[0].message.content

        # --- Show result in app ---
        st.success("✅ Datasheet successfully generated!")
        st.markdown("### 📘 Datasheet Preview")
        st.markdown(datasheet)

        # --- DOCX export ---
        docx_buffer = BytesIO()
        doc = Document()
        if company_logo:
            from PIL import Image
            from docx.shared import Inches
            image = Image.open(company_logo)
            image_path = "/tmp/logo.png"
            image.save(image_path)

    doc.add_picture(image_path, width=Inches(1.5))

        for line in datasheet.splitlines():
            if line.startswith("###") or line.startswith("##") or line.startswith("#"):
                doc.add_heading(line.strip("# "), level=2)
            elif line.startswith("-"):
                doc.add_paragraph(line.strip("- "), style="List Bullet")
            else:
                doc.add_paragraph(line)
        doc.save(docx_buffer)
        st.download_button(
            label="⬇️ Download as DOCX",
            data=docx_buffer.getvalue(),
            file_name="datasheet.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        # --- PDF export ---
        pdf = FPDF()
        pdf.add_page()
        if company_logo:
            import tempfile
            logo_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            logo_temp.write(company_logo.getvalue())
            logo_temp.flush()
            pdf.image(logo_temp.name, x=10, y=8, w=30)
            pdf.set_y(30)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=11)
        for line in datasheet.splitlines():
            pdf.multi_cell(0, 10, line)
        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer)
        st.download_button(
            label="⬇️ Download as PDF",
            data=pdf_buffer.getvalue(),
            file_name="datasheet.pdf",
            mime="application/pdf"
        )

        # --- TXT export ---
        st.download_button(
            label="⬇️ Download as TXT",
            data=datasheet,
            file_name="datasheet.txt",
            mime="text/plain"
        )
