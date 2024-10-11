# services/describe_image.py

import streamlit as st
from utils.server_utils import describe_image

def run():
    st.title("Image Description")
    st.subheader("Upload an image, and the app will generate a description for the image.")

    uploaded_file = st.sidebar.file_uploader("Choose an image...", ["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        img_bytes = uploaded_file.read()

        if st.sidebar.button("Generate Description"):
            with st.spinner("Generating description..."):
                try:
                    # Call a function or API that returns a description for the image
                    description = describe_image(img_bytes)  
                    st.success("Description generated successfully!")
                    st.write(f"**Description:** {description}")
                except ValueError as e:
                    st.error(f"Error: {str(e)}")
