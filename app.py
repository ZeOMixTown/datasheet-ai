import streamlit as st
import openai

st.set_page_config(page_title="Datasheet Generator", layout="centered")
st.title("📄 Datasheet Generator")

st.header("1. Enter product information")

product_name = st.text_input("Product name")
dimensions = st.text_input("Dimensions (e.g. 50×30×10 mm)")
weight = st.text_input("Weight")
power = st.text_input("Power supply (e.g. 3.3 V / 150 mA)")
features = st.text_area("Key features (comma separated)")
applications = st.text_area("Target applications (comma separated)")

st.divider()

st.header("2. Generate your datasheet")

if st.button("Generate with AI"):
    with st.spinner("Generating datasheet..."):

        # ✅ GPT PROMPT
        prompt = f"""
        Create a short professional datasheet based on the following product details:

        Name: {product_name}
        Dimensions: {dimensions}
        Weight: {weight}
        Power: {power}
        Features: {features}
        Applications: {applications}

        Include:
        - A short description
        - A bullet list of key features
        - A list of use cases
        - Present it in clean markdown formatting.
        """

        openai.api_key = st.secrets["OPENAI_API_KEY"]  # безопасно хранить в secrets

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical writer."},
                {"role": "user", "content": prompt}
            ]
        )
        datasheet = response["choices"][0]["message"]["content"]
        st.success("Done!")
        st.markdown("### ✨ Generated Datasheet")
        st.markdown(datasheet)

        # Download as .txt
        st.download_button("Download as .txt", data=datasheet, file_name="datasheet.txt")
