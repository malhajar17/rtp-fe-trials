# services/resize_with_bleed.py

import streamlit as st
import constants as const
import image_calc_utils as img_utils

def run():
    # Get the uploaded file from session state or upload new
    uploaded_file = st.sidebar.file_uploader("Choose an image...", ["jpg", "png", "jpeg"])

    resize_type = st.sidebar.radio("Resize Type", ["Custom Dimensions", "Standard Resize"])

    if resize_type == "Custom Dimensions":
        st.title("Image Resize with Custom Dimensions")
        st.subheader("Upload an image and specify the base dimensions. The app will resize your image accordingly.")

        if uploaded_file is not None:
            img_bytes = uploaded_file.read()  # Read the file only once and reuse the bytes

            initial_width_mm, initial_height_mm, initial_width_px, initial_height_px = img_utils.get_initial_dimensions(img_bytes)

            # Base dimensions input by user
            base_width_mm = st.sidebar.number_input("Base Width (mm)", min_value=float(const.MIN_DIMENSION), value=float(initial_width_mm), step=1.0)
            base_height_mm = st.sidebar.number_input("Base Height (mm)", min_value=float(const.MIN_DIMENSION), value=float(initial_height_mm), step=1.0)

            # Move resize_option here so it's chosen before processing
            resize_option = st.sidebar.radio("Image is larger than specified dimensions. Choose an option:", ["Scale Down and Fill Bleed", "Crop Image"])

            if st.sidebar.button("Process Image"):
                with st.spinner("Processing your image..."):
                    img_utils.process_and_display_image(img_bytes, base_width_mm, base_height_mm, resize_option)

    elif resize_type == "Standard Resize":
        st.title("Standard Image Resize")
        st.subheader("Upload an image and choose a standard format. The app will resize your image to match the selected format and add the bleed.")

        if uploaded_file is not None:
            img_bytes = uploaded_file.read()  # Read the file only once and reuse the bytes

            # Get initial dimensions in both mm and pixels
            initial_width_mm, initial_height_mm, initial_width_px, initial_height_px = img_utils.get_initial_dimensions(img_bytes)
            # Select orientation first
            orientation = st.sidebar.radio("Choose orientation", ["Portrait", "Paysage"])

            # Determine the list of available formats based on the orientation
            available_formats = [f for f in const.FORMATS.keys() if orientation.lower() in f.lower()]

            # Select format based on the chosen orientation
            format_choice = st.sidebar.selectbox("Choose a format", available_formats)

            # Get dimensions and bleed based on the selected format
            dimensions, bleed_dimensions = const.FORMATS.get(format_choice)
            format_width_mm = dimensions[0]
            format_height_mm = dimensions[1]

            # Convert format dimensions to pixels at 300 DPI
            format_width_px = int((format_width_mm / 25.4) * 300)
            format_height_px = int((format_height_mm / 25.4) * 300)

            # Check if image is larger than the specified dimensions
            if initial_width_px > format_width_px or initial_height_px > format_height_px:
                resize_option = st.sidebar.radio("Image is larger than specified dimensions. Choose an option:", ["Scale Down and Fill Bleed", "Crop Image"])
            else:
                resize_option = None  # No need to choose, image will just be resized

            st.sidebar.info(f"Selected Format: {format_choice}")
            st.sidebar.info(f"Base dimensions: {int(initial_width_mm)} mm x {int(initial_height_mm)} mm")
            st.sidebar.info(f"Final dimensions with Bleed mm: {format_width_mm} mm x {format_height_mm} mm")

            if st.sidebar.button("Process Image"):
                with st.spinner("Processing your image..."):
                    img_utils.process_and_display_image(img_bytes, format_width_px, format_height_px, resize_option)
