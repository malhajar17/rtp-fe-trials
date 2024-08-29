import streamlit as st
from server_utils import generate_flyer_image, remove_background, upscale_image, download_image, resize_with_bleed
import elements as ui
import constants as const  # Import your constants
from io import BytesIO
import utils  # Import the utils module
import image_calc_utils as img_utils

# Streamlit page configuration
st.set_page_config(
    page_title="Image Processing App",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Load custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the custom CSS file
load_css(const.STYLE_FILE)

# Sidebar for user inputs
st.sidebar.title("Image Processing Controls")
uploaded_file = st.sidebar.file_uploader("Choose an image...", ["jpg", "png", "jpeg"])

# Select service: Upscale or Resize with Bleed
service_choice = st.sidebar.radio("Choose a service", ["Upscale Image", "Resize with Bleed", "Remove Background", "Generate Flyer"])

if service_choice == "Upscale Image":
    upscale_factor = st.sidebar.slider("Upscale Factor", const.MIN_UPSCALE_FACTOR, const.MAX_UPSCALE_FACTOR, const.DEFAULT_UPSCALE_FACTOR)
    st.sidebar.info("Use the slider to select how much you want to upscale your image.")

    st.title("Image Upscaler")
    st.subheader("Upload an image and choose an upscale factor. The app will enhance your image and provide a download link.")

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

elif service_choice == "Resize with Bleed":
    resize_type = st.sidebar.radio("Resize Type", ["Custom Dimensions", "Standard Resize"])

    if resize_type == "Custom Dimensions":
        st.title("Image Resize with Custom Dimensions")
        st.subheader("Upload an image and specify the base dimensions. The app will resize your image accordingly.")

        # Get initial dimensions from the image or use defaults
        initial_width_mm, initial_height_mm = img_utils.get_initial_dimensions(uploaded_file)

        # Base dimensions input by user
        base_width_mm = st.sidebar.number_input("Base Width (mm)", min_value=float(const.MIN_DIMENSION), value=float(initial_width_mm), step=1.0)
        base_height_mm = st.sidebar.number_input("Base Height (mm)", min_value=float(const.MIN_DIMENSION), value=float(initial_height_mm), step=1.0)

        if uploaded_file is not None:
            img_bytes = uploaded_file.read()

            if st.sidebar.button("Process Image"):
                with st.spinner("Processing your image..."):
                    img_utils.process_and_display_image(img_bytes, base_width_mm, base_height_mm)

    elif resize_type == "Standard Resize":
        st.title("Standard Image Resize")
        st.subheader("Upload an image and choose a standard format. The app will resize your image to match the selected format and add the bleed.")

        # Select orientation first
        orientation = st.sidebar.radio("Choose orientation", ["Portrait", "Paysage"])

        # Determine the list of available formats based on the orientation
        available_formats = [f for f in const.FORMATS.keys() if orientation.lower() in f]

        # Select format based on the chosen orientation
        format_choice = st.sidebar.selectbox("Choose a format", available_formats)

        # Get dimensions and bleed based on the selected format
        dimensions, bleed_dimensions = const.FORMATS.get(format_choice)
        format_width_mm = bleed_dimensions[0]
        format_height_mm = bleed_dimensions[1]
        initial_width_mm, initial_height_mm = img_utils.get_initial_dimensions(uploaded_file)  
        st.sidebar.info(f"Selected Format: {format_choice}")
        st.sidebar.info(f"Original Image dimensions: {round(initial_width_mm)} mm x {round(initial_height_mm)} mm")
        st.sidebar.info(f"Final dimensions with Bleed: {format_width_mm} mm x {format_height_mm} mm")

        if uploaded_file is not None:
            img_bytes = uploaded_file.read()

            if st.sidebar.button("Process Image"):
                with st.spinner("Processing your image..."):
                    img_utils.process_and_display_image(img_bytes, format_width_mm, format_height_mm)

elif service_choice == "Remove Background":
    st.title("Background Remover")
    st.subheader("Upload an image, and the app will remove its background.")

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

elif service_choice == "Generate Flyer":
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
