import streamlit as st
import openai

st.set_page_config(page_title="Datasheet Generator", layout="centered")
st.title("📄 Datasheet Generator")

# --- User input section ---
st.header("1. Enter product information")

product_name = st.text_input("Product name")
dimensions = st.text_input("Dimensions (e.g. 50×30×10 mm)")
weight = st.text_input("Weight")
power = st.text_input("Power supply (e.g. 3.3 V / 150 mA)")
features = st.text_area("Key features (comma separated)")
applications = st.text_area("Target applications (comma separated)")

st.divider()
st.header("2. Generate your datasheet")

# --- GPT generation ---
if st.button("Generate with AI"):
    with st.spinner("Generating datasheet..."):

        # Build prompt
        prompt = f"""
You are a professional technical writer specializing in electronics documentation.
Generate a concise and technically accurate datasheet for an electronic product.
The datasheet must comply with industrial documentation standards (e.g. IEC, JEDEC, IPC) and be structured as follows:

---
**1. Product Overview**  
A 1–2 sentence summary of the device’s function and key attributes. Avoid marketing tone. Be objective.

**2. Key Features**  
A bullet list (5–10 points) describing core specifications or functions, e.g. voltage range, communication interfaces, protection features, mounting type.

**3. Mechanical Specifications**  
- Dimensions (in mm, formatted as Width × Height × Depth)
- Weight (in grams)
- Enclosure type (if relevant)
- Mounting type (e.g. SMD, THT, DIN rail, panel-mounted)

**4. Electrical Characteristics**  
- Operating voltage range (e.g. 3.0 V – 3.6 V)
- Supply current or power consumption
- Communication interfaces (e.g. UART, I2C, SPI)
- Max load (e.g. output current or switching power)

**5. Environmental Ratings**  
- Operating temperature range (°C)
- Storage temperature range (optional)
- IP protection level (if relevant)
- Humidity tolerance (optional)

**6. Regulatory & Compliance**  
- CE / FCC / RoHS status
- ESD protection (if applicable)
- Safety certifications (e.g. UL 94V-0)

**7. Applications**  
Bullet list of common use cases or application domains (e.g. battery-powered devices, industrial monitoring, IoT nodes)

---

**Formatting Instructions:**
- Use markdown
- Do not include unnecessary creative phrases
- Use SI units consistently
- Never guess unspecified values
- If a value is missing, omit the line

---
Input component information:
Name: {product_name}
Dimensions: {dimensions}
Weight: {weight}
Power: {power}
Features: {features}
Applications: {applications}
"""


        # Load API key from secrets (defined in Streamlit Cloud or .streamlit/secrets.toml)
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        # Use the new V1 chat API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical writer."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract generated text
        datasheet = response.choices[0].message.content

        # Display result
        st.success("Done!")
        st.markdown("### ✨ Generated Datasheet")
        st.markdown(datasheet)

        # Add download button
        st.download_button("Download as .txt", data=datasheet, file_name="datasheet.txt")
