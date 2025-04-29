import streamlit as st
import openai
from docx import Document
from docx.shared import Pt, Inches
from io import BytesIO
from fpdf import FPDF
from PIL import Image
import tempfile

# --- Streamlit page settings ---
st.set_page_config(page_title="Datasheet Generator", layout="centered")
st.title("\U0001F4C4 AI-Based Datasheet Generator")

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

# Optional custom parameters
st.markdown("#### ➕ Optional Custom Parameters")

# Dictionary to store custom key-value fields
custom_fields = {}

# User selects how many custom fields to define
custom_count = st.number_input("How many custom fields?", min_value=0, max_value=10, step=1)

# Dynamically render input fields based on user's selection
for i in range(int(custom_count)):
    col1, col2 = st.columns(2)
    with col1:
        field_name = st.text_input(f"Field #{i+1} - Name", key=f"cf_key_{i}")
    with col2:
        field_value = st.text_input(f"Field #{i+1} - Value", key=f"cf_val_{i}")
    
    # Only include filled fields
    if field_name and field_value:
        custom_fields[field_name] = field_value


for i in range(int(custom_count)):
    field_name = st.text_input(f"Custom Field #{i+1} Name", key=f"cf_key_{i}")
    field_value = st.text_input(f"Custom Field #{i+1} Value", key=f"cf_val_{i}")
    if field_name and field_value:
        custom_fields[field_name] = field_value

# --- Datasheet generation with GPT ---
if st.button("\U0001F527 Generate Datasheet"):
    with st.spinner("Generating content with GPT..."):

        # Prompt with structure and optional fields
        prompt = f"""
You are a professional technical writer specializing in sensor datasheets for electronic devices.
Generate a precise and technically accurate datasheet in clean markdown format.
The datasheet must comply with industrial documentation standards (IEC, JEDEC, IPC) and be structured as follows:

---

### 1. Product Overview
Provide a short, factual description (1–2 sentences) of the sensor’s purpose and main capabilities.

### 2. Key Features
Provide 5–10 concise bullet points with product highlights.

### 3. Mechanical Specifications
- Dimensions: {dimensions}
- Weight: {weight}
- Mounting Type (if applicable)

### 4. Electrical Characteristics
- Power Supply: {power}
- Output Signal Type: {signal_type}

### 5. Sensing Performance
- Measurement Range: {measurement_range}
- Sensitivity: {sensitivity}
- Accuracy: {accuracy}
- Response Time: {response_time}

### 6. Environmental Ratings
Include any applicable items (e.g., operating temp, IP rating).

### 7. Regulatory & Compliance
Include certification standards such as CE, FCC, RoHS, ESD protection.

### 8. Applications
{applications}

### 9. Additional Specifications
"""
        for k, v in custom_fields.items():
            prompt += f"- {k}: {v}\n"

        prompt += """

---

**Formatting instructions:**
- Use markdown headings and bullet points.
- Keep tone technical and formal.
- Use SI units.
- Do not guess missing values.

---
Product Name: {product_name}
Sensor Type: {sensor_type}
Features: {features}
"""

        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a technical writer."},
                {"role": "user", "content": prompt}
            ]
        )

        datasheet = response.choices[0].message.content

        st.success("✅ Datasheet successfully generated!")
        st.markdown("### 📘 Datasheet Preview")
        st.markdown(datasheet)

        # DOCX Export
        docx_buffer = BytesIO()
        doc = Document()
        if company_logo:
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
        st.download_button("⬇️ Download as DOCX", data=docx_buffer.getvalue(), file_name="datasheet.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        # PDF Export
        pdf = FPDF()
        pdf.add_page()
        if company_logo:
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
        st.download_button("⬇️ Download as PDF", data=pdf_buffer.getvalue(), file_name="datasheet.pdf", mime="application/pdf")

        # TXT Export
        st.download_button("⬇️ Download as TXT", data=datasheet, file_name="datasheet.txt", mime="text/plain")
