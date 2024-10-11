# services/upscale_image.py

import streamlit as st
import constants as const
from io import BytesIO
from utils.server_utils import upscale_image

def run():
    st.sidebar.info("Use the slider to select how much you want to upscale your image.")
    upscale_factor = st.sidebar.slider("Upscale Factor", const.MIN_UPSCALE_FACTOR, const.MAX_UPSCALE_FACTOR, const.DEFAULT_UPSCALE_FACTOR)
    
    st.title("Image Upscaler")
    st.subheader("Upload an image and choose an upscale factor. The app will enhance your image and provide a download link.")

    uploaded_file = st.sidebar.file_uploader("Choose an image...", ["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Original Image", use_column_width=True)
        img_bytes = uploaded_file.read()

        if st.sidebar.button("Process Image"):
            with st.spinner("Upscaling your image..."):
                try:
                    upscaled_image, s3_key = upscale_image(const.UPSCALE_SERVICE_URL, img_bytes, upscale_factor)

                    # Convert PIL image to bytes
                    buffered = BytesIO()
                    upscaled_image.save(buffered, format="PNG")
                    image_bytes = buffered.getvalue()
                    if upscaled_image:
                        st.success("Image upscaled successfully!")
                        st.image(upscaled_image, caption="Upscaled Image", use_column_width=True)
                        st.download_button(
                            label="Download Upscaled Image",
                            data=image_bytes,
                            file_name=s3_key.split("/")[-1],
                            mime="image/png"
                        )
                    else:
                        st.error("Could not download the image.")
                except ValueError as e:
                    st.error(f"Error: {str(e)}")
