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

product_name = st.text_input("Product Name")
dimensions = st.text_input("Dimensions (e.g., 50×30×10 mm)")
weight = st.text_input("Weight (g)")
power = st.text_input("Power Supply (e.g., 3.3 V / 150 mA)")
features = st.text_area("Key Features (comma separated)")
applications = st.text_area("Target Applications (comma separated)")

st.divider()
st.header("2. Generate AI Datasheet")

# --- Datasheet generation with GPT ---
if st.button("🔧 Generate Datasheet"):
    with st.spinner("Generating content with GPT..."):

        # Prompt template with proper structure and formatting instructions
        prompt = f"""
You are a professional technical writer specializing in electronics documentation.
Generate a concise and technically accurate datasheet for an electronic product.
The datasheet must comply with industrial documentation standards (IEC, JEDEC, IPC) and be structured as follows:

1. Product Overview
2. Key Features (bullet points)
3. Mechanical Specifications
4. Electrical Characteristics
5. Environmental Ratings
6. Regulatory & Compliance
7. Applications

Formatting instructions:
- Use clear section headers.
- Use bullet lists or markdown tables where appropriate.
- Keep it factual and concise.
- Use SI units.
- Do not guess values.

Component Info:
Name: {product_name}
Dimensions: {dimensions}
Weight: {weight}
Power: {power}
Features: {features}
Applications: {applications}
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
        doc.add_heading(product_name or "Datasheet", 0)
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
