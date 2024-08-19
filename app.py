import streamlit as st
from server_utils import remove_background, upscale_image, download_image, resize_with_bleed
import elements as ui
import constants as const
from io import BytesIO

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
service_choice = st.sidebar.radio("Choose a service", ["Upscale Image", "Resize with Bleed", "Remove Background"])

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
    # Initially, set the base dimensions from the uploaded image size (assuming you know these)
    if uploaded_file is not None:
        # Assuming these are the dimensions in mm from the image metadata or another source
        image_metadata = st.image(uploaded_file, caption="Original Image", use_column_width=True)
        initial_width_mm = 100  # Replace with actual image width in mm
        initial_height_mm = 150  # Replace with actual image height in mm
    else:
        initial_width_mm = 100  # Default if no image is uploaded yet
        initial_height_mm = 150  # Default if no image is uploaded yet

    # Bleed slider and calculation
    bleed_mm = st.sidebar.slider("Bleed Margin (mm)", 0, const.MAX_BLEED_MARGIN, 0)

    # Adjust base dimensions based on the bleed
    base_width_mm = initial_width_mm + 2 * bleed_mm
    base_height_mm = initial_height_mm + 2 * bleed_mm

    # Display the base dimensions reflecting the bleed
    st.sidebar.number_input("Base Width (mm)", value=base_width_mm, disabled=True)
    st.sidebar.number_input("Base Height (mm)", value=base_height_mm, disabled=True)

    st.sidebar.info(f"Final dimensions with bleed: {base_width_mm} mm x {base_height_mm} mm")

    st.title("Image Resize with Bleed")
    st.subheader("Upload an image and specify the base dimensions and bleed margin. The app will resize your image and add the bleed.")

    if uploaded_file is not None:
        img_bytes = uploaded_file.read()

        if st.sidebar.button("Process Image"):
            with st.spinner("Resizing your image with bleed..."):
                try:
                    # Use the adjusted dimensions for the resize function
                    resized_image, image_bytes = resize_with_bleed(img_bytes, base_width_mm, base_height_mm, bleed_mm)
                    # Convert PIL image to bytes
                    buffered = BytesIO()
                    resized_image.save(buffered, format="PNG")
                    image_bytes = buffered.getvalue()
                    if resized_image:
                        st.success("Image resized with bleed successfully!")
                        st.image(resized_image, caption="Resized Image", use_column_width=True)
                        st.download_button(
                            label="Download Resized Image",
                            data=image_bytes,
                            file_name="resized_image.png",
                            mime="image/png"
                        )
                    else:
                        st.error("Could not download the image.")
                except ValueError as e:
                    st.error(f"Error: {str(e)}")

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
