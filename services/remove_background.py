# services/remove_background.py

import streamlit as st
from PIL import Image
from io import BytesIO
import base64
from utils.server_utils import remove_background
import elements as ui

def run():
    st.title("Background Remover")
    st.subheader("Upload an image, and the app will remove its background.")

    uploaded_file = st.sidebar.file_uploader("Choose an image...", ["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Original Image", use_column_width=True)
        img_bytes = uploaded_file.read()

        if st.sidebar.button("Process Image"):
            with st.spinner("Removing the background..."):
                try:
                    bg_removed_image, image_bytes = remove_background(img_bytes)
                    buffered = BytesIO()
                    bg_removed_image.save(buffered, format="PNG")
                    image_bytes = buffered.getvalue()
                    # Create checkerboard background
                    width, height = bg_removed_image.size
                    checkerboard = ui.create_checkerboard(width, height)

                    # Overlay the image onto the checkerboard
                    checkerboard.paste(bg_removed_image, (0, 0), bg_removed_image)

                    st.success("Background removed successfully!")
                    st.image(checkerboard, caption="Background Removed Image", use_column_width=True)
                    st.download_button(
                        label="Download Image with Background Removed",
                        data=image_bytes,
                        file_name="bg_removed_image.png",
                        mime="image/png"
                    )
                except ValueError as e:
                    st.error(f"Error: {str(e)}")
