import streamlit as st
from server_utils import upscale_image, download_image, resize_with_bleed
import elements as ui
import constants as const

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
service_choice = st.sidebar.radio("Choose a service", ["Upscale Image", "Resize with Bleed"])

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

                    if upscaled_image:
                        st.success("Image upscaled successfully!")
                        st.image(upscaled_image, caption="Upscaled Image", use_column_width=True)
                        st.download_button(
                            label="Download Upscaled Image",
                            data=img_bytes,
                            file_name=s3_key.split("/")[-1],
                            mime="image/png"
                        )
                    else:
                        st.error("Could not download the image.")
                except ValueError as e:
                    st.error(f"Error: {str(e)}")

elif service_choice == "Resize with Bleed":
    width = st.sidebar.number_input("Target Width (px)", const.MIN_DIMENSION)
    height = st.sidebar.number_input("Target Height (px)", const.MIN_DIMENSION)
    bleed = st.sidebar.slider("Bleed Margin (px)", 0, const.MAX_BLEED_MARGIN, const.DEFAULT_BLEED_MARGIN)
    st.sidebar.info("Specify the target dimensions and bleed margin.")

    st.title("Image Resize with Bleed")
    st.subheader("Upload an image and specify the target dimensions and bleed margin. The app will resize your image and add the bleed.")

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Original Image", use_column_width=True)

        img_bytes = uploaded_file.read()

        if st.sidebar.button("Process Image"):
            with st.spinner("Resizing your image with bleed..."):
                s3_link = resize_with_bleed(const.RESIZE_WITH_BLEED_SERVICE_URL, img_bytes, width, height, bleed)

            if s3_link:
                resized_image, image_bytes = download_image(s3_link)

                if resized_image:
                    st.success("Image resized with bleed successfully!")
                    st.image(resized_image, caption="Resized Image", use_column_width=True)
                    st.download_button(
                        label="Download Resized Image",
                        data=image_bytes,
                        file_name=s3_link.split("/")[-1],
                        mime="image/png"
                    )
                else:
                    st.error("Could not download the image.")
            else:
                st.error("Error in resizing the image.")
    else:
        st.info("Please upload an image to get started.")
