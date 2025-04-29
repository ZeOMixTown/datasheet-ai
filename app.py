import streamlit as st

import streamlit as st

st.title("Datasheet Generator")

product_name = st.text_input("Product name")
dimensions = st.text_input("Dimensions (e.g. 50x30x10 mm)")
weight = st.text_input("Weight")
power = st.text_input("Power supply")
features = st.text_area("Key features")
applications = st.text_area("Applications")

if st.button("Generate"):
    datasheet = f"""
    **Product Name:** {product_name}

    **Dimensions:** {dimensions}  
    **Weight:** {weight}  
    **Power Supply:** {power}  

    **Key Features:**  
    {features}

    **Applications:**  
    {applications}
    """
    st.markdown(datasheet)
