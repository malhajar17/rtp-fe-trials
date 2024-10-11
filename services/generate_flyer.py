# services/generate_flyer.py

import streamlit as st
from io import BytesIO
from utils.server_utils import generate_flyer_image

def run():
    st.title("Flyer Generator")
    st.subheader("Enter the details to generate your flyer image.")

    # Text field for flyer content
    flyer_text = st.text_area("Enter the flyer text here:", "Your flyer content goes here.")
    
    # Text field for flyer design
    flyer_design = st.text_area("Enter the flyer design instructions here:", "E.g., vibrant colors, modern style, minimalistic design, etc.")

    if flyer_text and flyer_design:
        if st.sidebar.button("Generate Flyer"):
            with st.spinner("Generating your flyer..."):
                try:
                    # Combine the text and design instructions into one prompt
                    flyer_prompt = f"Design a flyer with the following text: '{flyer_text}'. Design instructions: {flyer_design}."

                    flyer_image, s3_key = generate_flyer_image(flyer_prompt)

                    # Convert PIL image to bytes
                    buffered = BytesIO()
                    flyer_image.save(buffered, format="PNG")
                    image_bytes = buffered.getvalue()
                    if flyer_image:
                        st.success("Flyer generated successfully!")
                        st.image(flyer_image, caption="Generated Flyer", use_column_width=True)
                        st.download_button(
                            label="Download Flyer",
                            data=image_bytes,
                            file_name=s3_key.split("/")[-1],
                            mime="image/png"
                        )
                    else:
                        st.error("Could not download the flyer image.")
                except ValueError as e:
                    st.error(f"Error: {str(e)}")
